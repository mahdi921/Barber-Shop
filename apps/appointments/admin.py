"""Admin configuration for appointments app."""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Appointment
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'stylist', 'jalali_date', 'appointment_time', 
        'status', 'created_at'
    ]
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['customer__first_name', 'customer__last_name', 'stylist__first_name']
    readonly_fields = ['jalali_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات نوبت', {
            'fields': ('customer', 'stylist', 'service', 'appointment_date', 'jalali_date', 'appointment_time', 'status')
        }),
        ('یادداشت‌ها', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('لغو', {
            'fields': ('cancelled_at', 'cancelled_by')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at')
        }),
    )

