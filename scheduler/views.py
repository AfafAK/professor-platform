import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from core.forms import ContactForm
from .models import AppointmentSlot
from analytics.utils import log_page_view

def contact(request):
    log_page_view(request, "Contact et RDV")
    from django.conf import settings
    import urllib.request
    import urllib.parse
    import json

    if request.method == "POST":
        form = ContactForm(request.POST)

        # Verify reCAPTCHA
        recaptcha_response = request.POST.get('g-recaptcha-response')

        if settings.DEBUG:
            # Bypass reCAPTCHA verification in development/debug mode
            recaptcha_valid = True
        else:
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }

            recaptcha_valid = False
            try:
                data = urllib.parse.urlencode(values).encode()
                req = urllib.request.Request(url, data=data)
                response = urllib.request.urlopen(req, timeout=5)
                result = json.loads(response.read().decode())
                recaptcha_valid = result.get('success', False)
            except Exception:
                # Fallback to bypass verification if network/Google service is unreachable
                recaptcha_valid = True

        if not recaptcha_valid:
            messages.error(request, "Veuillez valider le reCAPTCHA de sécurité.")
            return render(request, "scheduler/contact.html", {
                "form": form,
                "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY
            })

        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été envoyé avec succès ! Le professeur vous répondra dans les plus brefs délais.")
            return redirect("contact")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ContactForm()

    return render(request, "scheduler/contact.html", {
        "form": form,
        "recaptcha_site_key": settings.RECAPTCHA_SITE_KEY
    })


def get_slots(request):
    """API endpoint for FullCalendar.js to fetch appointment slots."""
    slots = AppointmentSlot.objects.all()
    events = []

    for slot in slots:
        # Style events based on booking status
        if not slot.is_booked:
            color = "#10b981" # Green
            title = "Libre"
        else:
            if slot.status == 'ACCEPTED':
                color = "#3b82f6" # Blue
                title = f"Accepté - {slot.student_name}"
            elif slot.status == 'REJECTED':
                color = "#ef4444" # Red
                title = f"Refusé - {slot.student_name}"
            else:
                color = "#f59e0b" # Orange/Yellow
                title = f"En attente - {slot.student_name}"

        events.append({
            "id": slot.id,
            "title": title,
            "start": slot.start_time.isoformat(),
            "end": slot.end_time.isoformat(),
            "backgroundColor": color,
            "borderColor": color,
            "textColor": "#ffffff",
            "extendedProps": {
                "isBooked": slot.is_booked,
                "status": slot.status,
                "studentName": slot.student_name,
                "studentEmail": slot.student_email,
                "notes": slot.student_notes
            }
        })

    return JsonResponse(events, safe=False)


@csrf_exempt
def book_slot(request, slot_id):
    """API endpoint to handle AJAX booking of a slot."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Méthode non autorisée."}, status=405)

    try:
        slot = AppointmentSlot.objects.get(id=slot_id)
    except AppointmentSlot.DoesNotExist:
        return JsonResponse({"success": False, "error": "Ce créneau n'existe pas."}, status=404)

    if slot.is_booked:
        return JsonResponse({"success": False, "error": "Ce créneau a déjà été réservé."}, status=400)

    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        notes = data.get("notes", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Données JSON invalides."}, status=400)

    if not name or not email:
        # Fallback to logged-in user if available and client sent empty info
        if request.user.is_authenticated:
            name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            email = request.user.email
        else:
            return JsonResponse({"success": False, "error": "Le nom et l'e-mail sont requis."}, status=400)

    # Perform booking
    slot.is_booked = True
    slot.status = 'PENDING'
    slot.student_name = name
    slot.student_email = email
    slot.student_notes = notes
    if request.user.is_authenticated:
        slot.student = request.user
    slot.save()

    from core.models import Notification
    Notification.objects.create(
        type='APPOINTMENT',
        title="Nouvelle demande de rendez-vous",
        message=f"L'étudiant {slot.student_name} ({slot.student_email}) a réservé un créneau pour le {slot.start_time.strftime('%d/%m/%Y à %H:%M')}."
    )

    return JsonResponse({"success": True, "message": "Le créneau a été réservé avec succès ! Une demande de confirmation a été envoyée au professeur."})
