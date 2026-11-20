from django.db import models

class Publication(models.Model):
    PUB_TYPES = [
        ('JOURNAL', 'Article de Revue'),
        ('CONF', 'Communication en Conférence'),
        ('BOOK', 'Livre ou Chapitre de Livre'),
        ('PATENT', 'Brevet'),
        ('OTHER', 'Autre publication'),
    ]

    title = models.CharField("Titre de la publication", max_length=300)
    authors = models.CharField("Auteurs", max_length=300, help_text="Ex: J. Doe, A. Smith")
    pub_type = models.CharField("Type", max_length=10, choices=PUB_TYPES, default='JOURNAL')
    journal_or_book = models.CharField("Journal / Conférence / Éditeur", max_length=250, help_text="Nom de la revue scientifique ou de la conférence")
    year = models.PositiveIntegerField("Année de publication")
    pages = models.CharField("Volume, numéros ou pages", max_length=50, blank=True)
    abstract = models.TextField("Résumé (Abstract)", blank=True)

    # Resources
    pdf_file = models.FileField("Fichier PDF (Article)", upload_to="publications/pdf/", blank=True, null=True)
    code_link = models.URLField("Lien vers le Code source (GitHub)", blank=True, null=True)
    data_link = models.URLField("Lien vers les Données", blank=True, null=True)
    doi = models.CharField("DOI (Identifiant)", max_length=100, blank=True, help_text="Ex: 10.1000/xyz123")

    class Meta:
        verbose_name = "Publication scientifique"
        verbose_name_plural = "Publications scientifiques"
        ordering = ["-year", "title"]

    def __str__(self):
        return f"({self.year}) {self.title[:80]}"


class ResearchProject(models.Model):
    STATUS_CHOICES = [
        ('PAST', 'Projet Terminé'),
        ('CURRENT', 'Projet en Cours'),
        ('FUTURE', 'Projet Futur / Opportunité'),
    ]

    title = models.CharField("Titre du projet", max_length=200)
    description = models.TextField("Description / Objectifs du projet")
    status = models.CharField("Statut", max_length=10, choices=STATUS_CHOICES, default='CURRENT')
    start_date = models.DateField("Date de début")
    end_date = models.DateField("Date de fin (Optionnelle)", blank=True, null=True)
    image = models.ImageField("Illustration du projet", upload_to="projects/", blank=True, null=True)
    partners = models.CharField("Partenaires académiques/industriels", max_length=350, blank=True, help_text="Ex: CNRS, INRIA, Université de Paris")
    funding = models.CharField("Financement / Subvention", max_length=150, blank=True, help_text="Ex: ANR, Horizon Europe")
    project_link = models.URLField("Lien du projet (Optionnel)", blank=True, null=True)

    class Meta:
        verbose_name = "Projet de recherche"
        verbose_name_plural = "Projets de recherche"
        ordering = ["status", "-start_date"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
