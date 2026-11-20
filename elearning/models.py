import uuid
from django.db import models
from django.contrib.auth.models import User

class Training(models.Model):
    title = models.CharField("Titre de la formation", max_length=200)
    description = models.TextField("Description globale")
    image = models.ImageField("Image d'illustration", upload_to="elearning/trainings/", blank=True, null=True)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)

    class Meta:
        verbose_name = "Formation en ligne"
        verbose_name_plural = "Formations en ligne"

    def __str__(self):
        return self.title

    def get_progress_for_user(self, user):
        """Calculates percentage of modules completed by the user in this training."""
        if not user.is_authenticated:
            return 0
        total_modules = self.modules.count()
        if total_modules == 0:
            return 100
        completed_count = StudentProgress.objects.filter(
            student=user,
            module__training=self,
            completed=True
        ).count()
        return int((completed_count / total_modules) * 100)


class Module(models.Model):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name="modules", verbose_name="Formation")
    title = models.CharField("Titre du module", max_length=200)
    description = models.TextField("Description / Contenu textuel", blank=True)
    video_url = models.URLField("Lien de la vidéo de formation", blank=True, null=True, help_text="Lien YouTube, Vimeo, etc.")
    downloadable_file = models.FileField("Support de module (PDF/ZIP)", upload_to="elearning/modules/", blank=True, null=True)
    order = models.PositiveIntegerField("Ordre d'affichage", default=1)

    class Meta:
        verbose_name = "Module de formation"
        verbose_name_plural = "Modules de formation"
        ordering = ["order"]

    def __str__(self):
        return f"{self.training.title} - M{self.order}: {self.title}"


class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_records", verbose_name="Étudiant")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="progress_records", verbose_name="Module")
    completed = models.BooleanField("Complété", default=False)
    completed_at = models.DateTimeField("Terminé le", auto_now=True)

    class Meta:
        verbose_name = "Progression Étudiant"
        verbose_name_plural = "Progressions Étudiants"
        unique_together = ("student", "module")

    def __str__(self):
        return f"{self.student.username} - {self.module.title} (Statut: {self.completed})"


class Quiz(models.Model):
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name="quiz", verbose_name="Module")
    title = models.CharField("Titre du Quiz", max_length=200)
    passing_score = models.PositiveIntegerField("Score de réussite (%)", default=70, help_text="Pourcentage de réponses correctes requis pour réussir (ex: 70)")

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"

    def __str__(self):
        return f"Quiz : {self.title} ({self.module.title})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", verbose_name="Quiz")
    text = models.TextField("Texte de la question")
    points = models.PositiveIntegerField("Points", default=1)

    class Meta:
        verbose_name = "Question de Quiz"
        verbose_name_plural = "Questions de Quiz"

    def __str__(self):
        return f"Q: {self.text[:50]}..."


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices", verbose_name="Question")
    text = models.CharField("Texte de l'option", max_length=255)
    is_correct = models.BooleanField("Est-ce la bonne réponse ?", default=False)

    class Meta:
        verbose_name = "Option de réponse"
        verbose_name_plural = "Options de réponse"

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"


class QuizSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_submissions", verbose_name="Étudiant")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submissions", verbose_name="Quiz")
    score = models.FloatField("Score obtenu (%)")
    passed = models.BooleanField("Réussi", default=False)
    submitted_at = models.DateTimeField("Soumis le", auto_now_add=True)

    class Meta:
        verbose_name = "Tentative de Quiz"
        verbose_name_plural = "Tentatives de Quiz"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}% - {'Réussi' if self.passed else 'Échoué'})"


class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates", verbose_name="Étudiant")
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name="certificates", verbose_name="Formation")
    code = models.CharField("Code unique du certificat", max_length=100, unique=True, default=uuid.uuid4)
    issued_at = models.DateTimeField("Généré le", auto_now_add=True)
    pdf_file = models.FileField("Certificat PDF", upload_to="elearning/certificates/", blank=True, null=True)

    class Meta:
        verbose_name = "Certificat"
        verbose_name_plural = "Certificats"
        unique_together = ("student", "training")

    def __str__(self):
        return f"Certificat {self.code} - {self.student.username} - {self.training.title}"
