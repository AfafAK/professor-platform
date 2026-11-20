from django.contrib import admin
from .models import Publication, ResearchProject

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "authors", "pub_type", "journal_or_book", "year")
    list_filter = ("pub_type", "year")
    search_fields = ("title", "authors", "journal_or_book", "abstract")
    ordering = ["-year", "title"]

@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("title", "description", "partners")
    ordering = ["status", "-start_date"]
