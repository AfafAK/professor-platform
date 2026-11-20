from django.contrib import admin
from .models import PageView, DownloadTracker

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("page_name", "user", "timestamp")
    list_filter = ("page_name", "timestamp")
    readonly_fields = ("page_name", "user", "timestamp")
    search_fields = ("page_name", "user__username")
    date_hierarchy = "timestamp"

@admin.register(DownloadTracker)
class DownloadTrackerAdmin(admin.ModelAdmin):
    list_display = ("resource", "user", "timestamp")
    list_filter = ("resource__subject", "timestamp")
    readonly_fields = ("resource", "user", "timestamp")
    search_fields = ("resource__title", "user__username")
    date_hierarchy = "timestamp"
