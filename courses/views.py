from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from .models import Subject, CourseResource
from analytics.models import DownloadTracker
from analytics.utils import log_page_view

def course_list(request):
    log_page_view(request, "Supports de cours")

    # Filter subjects by level if specified
    level_filter = request.GET.get('level')
    if level_filter and level_filter in dict(Subject.LEVEL_CHOICES):
        subjects = Subject.objects.filter(level=level_filter).prefetch_related('resources')
    else:
        subjects = Subject.objects.all().prefetch_related('resources')

    levels = Subject.LEVEL_CHOICES

    context = {
        "subjects": subjects,
        "levels": levels,
        "selected_level": level_filter,
    }
    return render(request, "courses/course_list.html", context)

def download_resource(request, resource_id):
    resource = get_object_or_404(CourseResource, id=resource_id)

    # Track the download event
    user = request.user if request.user.is_authenticated else None
    DownloadTracker.objects.create(resource=resource, user=user)

    if resource.file:
        try:
            return FileResponse(open(resource.file.path, 'rb'), as_attachment=True, filename=resource.file.name.split('/')[-1])
        except FileNotFoundError:
            raise Http404("Le fichier demandé n'existe plus sur le serveur.")
    elif resource.video_url:
        return redirect(resource.video_url)

    return redirect('course_list')

def view_resource(request, resource_id):
    resource = get_object_or_404(CourseResource, id=resource_id)

    # Track the view/read event (we count it in DownloadTracker as well to keep dashboard metrics comprehensive)
    user = request.user if request.user.is_authenticated else None
    DownloadTracker.objects.create(resource=resource, user=user)

    if resource.file:
        try:
            return FileResponse(open(resource.file.path, 'rb'), as_attachment=False)
        except FileNotFoundError:
            raise Http404("Le fichier demandé n'existe plus sur le serveur.")
    elif resource.video_url:
        return redirect(resource.video_url)

    return redirect('course_list')
