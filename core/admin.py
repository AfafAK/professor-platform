from django.contrib import admin
from .models import ProfessorProfile, News, ContactMessage

@admin.register(ProfessorProfile)
class ProfessorProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "title")
    fieldsets = (
        ("Présentation", {
            "fields": ("name", "title", "biography", "avatar")
        }),
        ("Expertise & Distinctions", {
            "fields": ("expertise", "distinctions")
        }),
        ("Réseaux Sociaux & Liens Académiques", {
            "fields": ("linkedin", "github", "twitter", "google_scholar")
        }),
    )

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "created_at", "updated_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    search_fields = ("name", "email", "subject", "message")
    date_hierarchy = "created_at"
