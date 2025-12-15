"""
Serializers for ratings and reviews with anonymous display.
"""
from rest_framework import serializers
from .models import Rating, Review
from apps.appointments.models import Appointment


class AnonymousRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for public rating display (anonymous).
    Does NOT expose customer information.
    """
    stylist_name = serializers.CharField(source='stylist.full_name', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'stylist_name', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']


class AnonymousReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for public review display (anonymous).
    Does NOT expose customer information.
    """
    stylist_name = serializers.CharField(source='stylist.full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'stylist_name', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']


class MyRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for customer's own ratings.
    Includes all fields for customer to view their submissions.
    """
    stylist_name = serializers.CharField(source='stylist.full_name', read_only=True)
    salon_name = serializers.CharField(source='stylist.salon.name', read_only=True)
    appointment_date = serializers.DateField(source='appointment.appointment_date', read_only=True)
    
    class Meta:
        model = Rating
        fields = [
            'id', 'stylist_name', 'salon_name', 'rating',
            'appointment_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MyReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for customer's own reviews.
    """
    stylist_name = serializers.CharField(source='stylist.full_name', read_only=True)
    salon_name = serializers.CharField(source='stylist.salon.name', read_only=True)
    appointment_date = serializers.DateField(source='appointment.appointment_date', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'stylist_name', 'salon_name', 'text',
            'appointment_date', 'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'is_approved', 'created_at']


class SubmitRatingSerializer(serializers.Serializer):
    """
    Serializer for submitting a rating and optional review.
    """
    appointment_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review_text = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    
    def validate_appointment_id(self, value):
        """Validate appointment exists and belongs to current user."""
        try:
            appointment = Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("نوبت یافت نشد")
        
        # Check appointment belongs to current user
        request = self.context.get('request')
        if appointment.customer.user != request.user:
            raise serializers.ValidationError("این نوبت متعلق به شما نیست")
        
        # Check appointment is completed
        if appointment.status != 'completed':
            raise serializers.ValidationError("فقط می‌توانید به نوبت‌های تکمیل شده امتیاز دهید")
        
        # Check not already rated
        if hasattr(appointment, 'rating'):
            raise serializers.ValidationError("قبلاً به این نوبت امتیاز داده‌اید")
        
        return value
    
    def create(self, validated_data):
        """Create rating and optionally review."""
        appointment_id = validated_data['appointment_id']
        rating_value = validated_data['rating']
        review_text = validated_data.get('review_text', '')
        
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Create rating
        rating = Rating.objects.create(
            customer=appointment.customer,
            stylist=appointment.stylist,
            appointment=appointment,
            rating=rating_value
        )
        
        # Create review if text provided
        review = None
        if review_text:
            review = Review.objects.create(
                customer=appointment.customer,
                stylist=appointment.stylist,
                appointment=appointment,
                text=review_text
            )
        
        return {'rating': rating, 'review': review}
