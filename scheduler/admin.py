from django.contrib import admin
from .models import AppointmentSlot

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ("start_time", "end_time", "is_booked", "student_name", "student_email")
    list_filter = ("is_booked", "start_time")
    search_fields = ("student_name", "student_email", "student_notes")
    ordering = ["start_time"]
