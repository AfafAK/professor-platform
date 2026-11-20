from django.db import models

class ProfessorProfile(models.Model):
    name = models.CharField("Nom complet", max_length=150)
    title = models.CharField("Titre professionnel", max_length=200, help_text="Ex: Professeur des Universités, Chercheur en IA")
    biography = models.TextField("Biographie / Parcours académique")
    expertise = models.TextField("Domaines d'expertise", help_text="Séparer les domaines par des virgules")
    distinctions = models.TextField("Distinctions & Prix", blank=True, help_text="Une distinction par ligne")
    avatar = models.ImageField("Photo de profil", upload_to="profile/", blank=True, null=True)

    # Social links
    linkedin = models.URLField("Lien LinkedIn", blank=True, null=True)
    github = models.URLField("Lien GitHub", blank=True, null=True)
    twitter = models.URLField("Lien Twitter/X", blank=True, null=True)
    google_scholar = models.URLField("Lien Google Scholar", blank=True, null=True)

    class Meta:
        verbose_name = "Profil du Professeur"
        verbose_name_plural = "Profil du Professeur"

    def __str__(self):
        return self.name

    def get_expertise_list(self):
        return [item.strip() for item in self.expertise.split(",") if item.strip()]

    def get_distinctions_list(self):
        return [item.strip() for item in self.distinctions.split("\n") if item.strip()]


from django.contrib.auth.models import User

class News(models.Model):
    title = models.CharField("Titre", max_length=250)
    slug = models.SlugField("Slug", unique=True, max_length=250)
    content = models.TextField("Contenu")
    image = models.ImageField("Image d'illustration", upload_to="news/", blank=True, null=True)
    is_published = models.BooleanField("Publié", default=True)
    is_pinned = models.BooleanField("Épinglé", default=False)
    views_count = models.PositiveIntegerField("Nombre de vues", default=0)
    published_at = models.DateTimeField("Date de publication", blank=True, null=True)
    created_at = models.DateTimeField("Date de création", auto_now_add=True)
    updated_at = models.DateTimeField("Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return self.title


class NewsAttachment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="attachments", verbose_name="Actualité")
    file = models.FileField("Fichier", upload_to="news/attachments/")
    uploaded_at = models.DateTimeField("Téléversé le", auto_now_add=True)

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="comments", verbose_name="Actualité")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="news_comments", verbose_name="Auteur (si connecté)")
    author_name = models.CharField("Nom de l'auteur", max_length=100)
    author_email = models.EmailField("E-mail de l'auteur", blank=True)
    content = models.TextField("Commentaire")
    is_approved = models.BooleanField("Approuvé", default=True)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commentaire de {self.author_name} sur {self.news.title}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('REGISTRATION', 'Nouvelle inscription étudiant'),
        ('APPOINTMENT', 'Demande de rendez-vous'),
        ('COMMENT', 'Nouveau commentaire'),
        ('QUIZ', 'Quiz complété'),
        ('CERTIFICATE', 'Certificat généré'),
    ]

    type = models.CharField("Type de notification", max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField("Titre", max_length=200)
    message = models.TextField("Message")
    is_read = models.BooleanField("Lu", default=False)
    created_at = models.DateTimeField("Reçu le", auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"


class ContactMessage(models.Model):
    name = models.CharField("Nom", max_length=100)
    email = models.EmailField("E-mail")
    subject = models.CharField("Sujet", max_length=200)
    message = models.TextField("Message")
    created_at = models.DateTimeField("Envoyé le", auto_now_add=True)

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message de {self.name} - {self.subject}"
