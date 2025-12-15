"""Admin configuration for ratings app."""
from django.contrib import admin
from .models import Rating, Review


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['stylist', 'rating', 'get_salon', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['stylist__first_name', 'stylist__last_name']
    readonly_fields = ['customer', 'stylist', 'appointment', 'created_at']
    
    def get_salon(self, obj):
        return obj.salon.name
    get_salon.short_description = 'سالن'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['stylist', 'get_salon', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['text', 'stylist__first_name']
    readonly_fields = ['customer', 'stylist', 'appointment', 'created_at']
    
    fields = ['stylist', 'text', 'is_approved', 'created_at']
    
    def get_salon(self, obj):
        return obj.salon.name
    get_salon.short_description = 'سالن'
