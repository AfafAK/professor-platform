from django.db import models
from django.contrib.auth.models import User
from courses.models import CourseResource

class PageView(models.Model):
    page_name = models.CharField("Nom de la page", max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Utilisateur")
    timestamp = models.DateTimeField("Date et heure", auto_now_add=True)

    class Meta:
        verbose_name = "Page vue"
        verbose_name_plural = "Pages vues"
        ordering = ["-timestamp"]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonyme"
        return f"{self.page_name} - {user_str} à {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


class DownloadTracker(models.Model):
    resource = models.ForeignKey(CourseResource, on_delete=models.CASCADE, related_name="downloads", verbose_name="Ressource")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Utilisateur")
    timestamp = models.DateTimeField("Téléchargé le", auto_now_add=True)

    class Meta:
        verbose_name = "Suivi de téléchargement"
        verbose_name_plural = "Suivi de téléchargements"
        ordering = ["-timestamp"]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonyme"
        return f"Téléchargement {self.resource.title} - {user_str} à {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
