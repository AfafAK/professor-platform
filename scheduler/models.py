from django.db import models
from django.contrib.auth.models import User

class AppointmentSlot(models.Model):
    start_time = models.DateTimeField("Heure de début")
    end_time = models.DateTimeField("Heure de fin")
    is_booked = models.BooleanField("Réservé", default=False)

    # Booking information
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments", verbose_name="Étudiant inscrit (si connecté)")
    student_name = models.CharField("Nom complet de l'étudiant", max_length=150, blank=True)
    student_email = models.EmailField("E-mail de l'étudiant", blank=True)
    student_notes = models.TextField("Notes / Objectif du rendez-vous", blank=True)

    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('ACCEPTED', 'Accepté'),
        ('REJECTED', 'Refusé'),
    ]
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        verbose_name = "Créneau de rendez-vous"
        verbose_name_plural = "Créneaux de rendez-vous"
        ordering = ["start_time"]

    def __str__(self):
        status = f"Réservé par {self.student_name or (self.student.username if self.student else 'Inconnu')}" if self.is_booked else "Libre"
        return f"{self.start_time.strftime('%d/%m/%Y %H:%M')} - {self.end_time.strftime('%H:%M')} ({status})"
