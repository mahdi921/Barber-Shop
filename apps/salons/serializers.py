from rest_framework import serializers
from .models import Salon, Service, WorkingHours
from apps.accounts.serializers import StylistProfileSerializer

class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Salon Services."""
    stylist_name = serializers.CharField(source='stylist.full_name', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'service_type', 'custom_name', 'price', 
            'duration_minutes', 'stylist', 'stylist_name'
        ]

class SalonSerializer(serializers.ModelSerializer):
    """Serializer for Salon listing and details."""
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    stylists = StylistProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Salon
        fields = [
            'id', 'name', 'photo', 'address', 'gender_type', 
            'average_rating', 'total_ratings', 'manager_name', 'services', 'stylists'
        ]

class WorkingHoursSerializer(serializers.ModelSerializer):
    """Serializer for Working Hours."""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = WorkingHours
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time']
