"""Admin configuration for salons app."""
from django.contrib import admin
from .models import Salon, Service, WorkingHours


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'gender_type', 'average_rating', 'total_ratings', 'created_at']
    list_filter = ['gender_type', 'created_at']
    search_fields = ['name', 'address', 'manager__salon_name']
    readonly_fields = ['average_rating', 'total_ratings', 'created_at', 'updated_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'salon', 'stylist', 'price', 'is_active']
    list_filter = ['service_type', 'is_active', 'salon__gender_type']
    search_fields = ['custom_name', 'salon__name']
    
    def get_name(self, obj):
        return obj.custom_name if obj.custom_name else obj.get_service_type_display()
    get_name.short_description = 'نام خدمت'


@admin.register(WorkingHours)
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['get_entity', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active']
    
    def get_entity(self, obj):
        return obj.salon.name if obj.salon else obj.stylist.full_name
    get_entity.short_description = 'سالن/آرایشگر'
