"""
Serializers for Salon Management API endpoints.
"""
from rest_framework import serializers
from .models import Salon, Service, WorkingHours
from apps.accounts.serializers import StylistProfileSerializer


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model."""
    stylist_name = serializers.CharField(source='stylist.full_name', read_only=True, allow_null=True)
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'service_type', 'service_type_display', 'custom_name',
            'price', 'duration_minutes', 'is_active', 'stylist', 'stylist_name'
        ]
        read_only_fields = ['id']


class WorkingHoursSerializer(serializers.ModelSerializer):
    """Serializer for WorkingHours model."""
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = WorkingHours
        fields = [
            'id', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'is_active'
        ]
        read_only_fields = ['id']


class SalonManagementSerializer(serializers.ModelSerializer):
    """Serializer for Salon management (editing)."""
    services = ServiceSerializer(many=True, read_only=True)
    working_hours = WorkingHoursSerializer(many=True, read_only=True)
    stylists = StylistProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Salon
        fields = [
            'id', 'name', 'address', 'gender_type', 'photo',
            'average_rating', 'total_ratings',
            'services', 'working_hours', 'stylists'
        ]
        read_only_fields = ['id', 'average_rating', 'total_ratings']
