"""
Serializers for appointments app with Jalali calendar support.
"""
from rest_framework import serializers
from .models import Appointment
from apps.accounts.serializers import CustomerProfileSerializer, StylistProfileSerializer
from apps.salons.models import Service
from .utils import jalali_to_gregorian, gregorian_to_jalali
from datetime import time


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments with Jalali date display."""
    jalali_date = serializers.ReadOnlyField()
    jalali_datetime_display = serializers.ReadOnlyField()
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    stylist_name = serializers.CharField(source='stylist.full_name', read_only=True)
    service_name = serializers.CharField(source='service.__str__', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'customer_name', 'stylist', 'stylist_name',
            'service', 'service_name', 'appointment_date', 'appointment_time',
            'jalali_date', 'jalali_datetime_display', 'status',
            'customer_notes', 'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'jalali_date']


class BookAppointmentSerializer(serializers.Serializer):
    """Serializer for booking appointments with Jalali date input."""
    stylist_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    jalali_date = serializers.CharField(help_text="Format: YYYY/MM/DD (e.g., 1402/09/20)")
    time_slot = serializers.TimeField(help_text="Format: HH:MM (e.g., 14:30)")
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate and convert Jalali date to Gregorian."""
        from apps.accounts.models import StylistProfile
        from django.shortcuts import get_object_or_404
        
        # Validate stylist exists
        stylist = get_object_or_404(StylistProfile, id=data['stylist_id'])
        data['stylist'] = stylist
        
        # Validate service exists and belongs to stylist's salon
        service = get_object_or_404(Service, id=data['service_id'])
        if service.salon != stylist.salon:
            raise serializers.ValidationError("این سرویس در سالن این آرایشگر ارائه نمی‌شود")
        data['service'] = service
        
        # Convert Jalali to Gregorian
        try:
            gregorian_date = jalali_to_gregorian(data['jalali_date'])
            data['appointment_date'] = gregorian_date
        except Exception as e:
            raise serializers.ValidationError(f"تاریخ نامعتبر است: {str(e)}")
        
        # Validate time slot format
        data['appointment_time'] = data['time_slot']
        
        return data
    
    def create(self, validated_data):
        """Create appointment with transaction safety."""
        from django.db import transaction
        
        # Get customer from context (current user)
        customer = self.context['request'].user.customer_profile
        
        # Remove helper fields
        stylist = validated_data.pop('stylist')
        service = validated_data.pop('service')
        validated_data.pop('stylist_id')
        validated_data.pop('service_id')
        validated_data.pop('jalali_date')
        validated_data.pop('time_slot')
        
        # Create with database lock to prevent double-booking
        with transaction.atomic():
            appointment = Appointment.objects.create(
                customer=customer,
                stylist=stylist,
                service=service,
                **validated_data
            )
        
        return appointment


class AvailabilityQuerySerializer(serializers.Serializer):
    """Serializer for availability query parameters."""
    stylist_id = serializers.IntegerField()
    jalali_date = serializers.CharField(help_text="Format: YYYY/MM/DD")
