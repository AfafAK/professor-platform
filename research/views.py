from django.shortcuts import render
from .models import Publication, ResearchProject
from analytics.utils import log_page_view

def research_and_publications(request):
    log_page_view(request, "Recherche et Publications")

    publications = Publication.objects.all().order_by("-year", "title")
    projects = ResearchProject.objects.all().order_by("status", "-start_date")

    # Group projects by status
    projects_by_status = {
        'current': [p for p in projects if p.status == 'CURRENT'],
        'past': [p for p in projects if p.status == 'PAST'],
        'future': [p for p in projects if p.status == 'FUTURE'],
    }

    context = {
        "publications": publications,
        "projects": projects_by_status,
    }
    return render(request, "research/research.html", context)
