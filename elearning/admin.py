from django.contrib import admin
from .models import Training, Module, StudentProgress, Quiz, Question, Choice, QuizSubmission, Certificate

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    ordering = ["order"]

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title", "description")
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "training", "order")
    list_filter = ("training",)
    search_fields = ("title", "description")
    ordering = ["training", "order"]

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "points")
    list_filter = ("quiz",)
    search_fields = ("text",)
    inlines = [ChoiceInline]

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "passing_score")
    search_fields = ("title", "module__title")
    inlines = [QuestionInline]

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "module", "completed", "completed_at")
    list_filter = ("completed", "module__training", "module")
    search_fields = ("student__username", "student__email", "module__title")

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "passed", "submitted_at")
    list_filter = ("passed", "quiz", "quiz__module__training")
    search_fields = ("student__username", "quiz__title")
    readonly_fields = ("student", "quiz", "score", "passed", "submitted_at")

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "student", "training", "issued_at")
    list_filter = ("training", "issued_at")
    search_fields = ("code", "student__username", "training__title")
    readonly_fields = ("code", "student", "training", "issued_at", "pdf_file")
