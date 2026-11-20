from django.contrib import admin
from .models import Subject, CourseResource

class CourseResourceInline(admin.TabularInline):
    model = CourseResource
    extra = 1

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "level")
    list_filter = ("level",)
    search_fields = ("code", "name", "description")
    inlines = [CourseResourceInline]

@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "resource_type", "uploaded_at")
    list_filter = ("resource_type", "subject__level", "subject")
    search_fields = ("title", "description", "subject__name", "subject__code")
    date_hierarchy = "uploaded_at"
