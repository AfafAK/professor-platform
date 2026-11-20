from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import ProfessorProfile, News
from .forms import StudentRegistrationForm
from analytics.utils import log_page_view

def home(request):
    log_page_view(request, "Accueil")
    profile = ProfessorProfile.objects.first()
    recent_news = News.objects.filter(is_published=True)[:3]
    context = {
        "profile": profile,
        "recent_news": recent_news,
    }
    return render(request, "core/home.html", context)

def register_student(request):
    log_page_view(request, "Inscription")
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            from core.models import Notification
            Notification.objects.create(
                type='REGISTRATION',
                title="Nouvelle inscription étudiant",
                message=f"L'étudiant {user.get_full_name() or user.username} ({user.email}) s'est inscrit sur la plateforme."
            )

            # Send email notifications
            from django.core.mail import send_mail
            from django.conf import settings
            try:
                send_mail(
                    subject="Bienvenue sur la plateforme Professeur",
                    message=f"Bonjour {user.get_full_name() or user.username},\n\nVotre inscription sur la plateforme a été complétée avec succès. Vous pouvez désormais vous connecter pour accéder à vos cours et formations.\n\nCordialement,\nL'administration.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            try:
                send_mail(
                    subject="Nouvelle inscription étudiant sur la plateforme",
                    message=f"L'étudiant {user.get_full_name() or user.username} ({user.email}) vient de créer son compte sur la plateforme.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

            login(request, user)
            messages.success(request, f"Compte étudiant créé avec succès ! Bienvenue, {user.username}.")
            return redirect("home")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = StudentRegistrationForm()

    return render(request, "core/register.html", {"form": form})
