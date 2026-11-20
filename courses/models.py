from django.db import models

class Subject(models.Model):
    LEVEL_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
        ('DOC', 'Doctorat'),
    ]

    name = models.CharField("Nom de la matière", max_length=150)
    code = models.CharField("Code du cours", max_length=10, unique=True, help_text="Ex: INF401, MAT302")
    level = models.CharField("Niveau", max_length=3, choices=LEVEL_CHOICES)
    description = models.TextField("Description de la matière", blank=True)
    thumbnail = models.ImageField("Miniature", upload_to="courses/thumbnails/", blank=True, null=True)
    is_published = models.BooleanField("Publié", default=True)
    is_archived = models.BooleanField("Archivé", default=False)

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ["level", "code"]

    def __str__(self):
        return f"[{self.code}] {self.name} ({self.get_level_display()})"


class CourseResource(models.Model):
    RESOURCE_TYPES = [
        ('COURS', 'Cours Magistral (PDF/Slides)'),
        ('TD', 'Travaux Dirigés (TD)'),
        ('TP', 'Travaux Pratiques (TP)'),
        ('EXAM', 'Annales / Examens'),
        ('SUPP', 'Lecture complémentaire / Ressource externe'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="resources", verbose_name="Matière")
    title = models.CharField("Titre du support", max_length=200)
    description = models.TextField("Description du contenu", blank=True)
    file = models.FileField("Document téléchargeable (PDF/Slides)", upload_to="courses/docs/", blank=True, null=True)
    video_url = models.URLField("Lien de vidéo (Optionnel)", blank=True, null=True, help_text="Lien YouTube, Vimeo, etc.")
    resource_type = models.CharField("Type de ressource", max_length=5, choices=RESOURCE_TYPES, default='COURS')
    download_count = models.PositiveIntegerField("Nombre de téléchargements", default=0)
    folder_name = models.CharField("Dossier", max_length=100, blank=True, help_text="Nom du sous-dossier d'organisation")
    uploaded_at = models.DateTimeField("Téléversé le", auto_now_add=True)

    class Meta:
        verbose_name = "Support de cours"
        verbose_name_plural = "Supports de cours"
        ordering = ["resource_type", "title"]

    def __str__(self):
        return f"{self.get_resource_type_display()} - {self.title} ({self.subject.code})"
