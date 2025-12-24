"""
REST Framework serializers for user authentication and profiles.
"""
from rest_framework import serializers
from .models import CustomUser, CustomerProfile, SalonManagerProfile, StylistProfile, SiteAdminProfile
from .validators import validate_iranian_phone


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for customer profiles."""
    jalali_date_of_birth = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'first_name', 'last_name', 'full_name',
            'selfie_photo', 'gender', 'date_of_birth',
            'jalali_date_of_birth', 'telegram_chat_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SalonManagerProfileSerializer(serializers.ModelSerializer):
    """Serializer for salon manager profiles."""
    
    class Meta:
        model = SalonManagerProfile
        fields = [
            'id', 'salon_name', 'salon_photo', 'salon_address',
            'salon_gender_type', 'telegram_chat_id', 'is_approved', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_approved', 'approved_at', 'created_at', 'updated_at']


class StylistProfileSerializer(serializers.ModelSerializer):
    """Serializer for stylist profiles."""
    jalali_date_of_birth = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = StylistProfile
        fields = [
            'id', 'salon', 'first_name', 'last_name', 'full_name',
            'gender', 'date_of_birth', 'jalali_date_of_birth',
            'telegram_chat_id', 'is_temporary', 'profile_completed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_temporary', 'profile_completed_at', 'created_at', 'updated_at']


class SiteAdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for site admin profiles."""
    
    class Meta:
        model = SiteAdminProfile
        fields = ['id', 'full_name', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model."""
    customer_profile = CustomerProfileSerializer(read_only=True)
    manager_profile = SalonManagerProfileSerializer(read_only=True)
    stylist_profile = StylistProfileSerializer(read_only=True)
    admin_profile = SiteAdminProfileSerializer(read_only=True)
    telegram_bot_username = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'user_type', 'is_phone_verified',
            'is_active', 'is_staff', 'date_joined',
            'customer_profile', 'manager_profile', 'stylist_profile', 'admin_profile',
            'telegram_bot_username'
        ]
        read_only_fields = ['id', 'date_joined', 'is_staff']
        
    def get_telegram_bot_username(self, obj):
        from django.conf import settings
        return settings.TELEGRAM_BOT_USERNAME


class CustomerRegistrationSerializer(serializers.Serializer):
    """Serializer for customer registration API."""
    phone_number = serializers.CharField(max_length=11, validators=[validate_iranian_phone])
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    selfie_photo = serializers.ImageField(required=False)
    gender = serializers.ChoiceField(choices=CustomerProfile.GENDER_CHOICES)
    date_of_birth = serializers.DateField()
    
    def validate(self, data):
        """Validate password confirmation."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نیستند")
            
        if CustomUser.objects.filter(phone_number=data['phone_number']).exists():
             raise serializers.ValidationError({"phone_number": "این شماره تلفن قبلاً ثبت شده است"})
            
        return data
    
    def create(self, validated_data):
        """Create user and customer profile."""
        # Remove password_confirm
        validated_data.pop('password_confirm')
        
        # Extract profile data
        profile_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'gender': validated_data.pop('gender'),
            'date_of_birth': validated_data.pop('date_of_birth'),
        }
        
        if 'selfie_photo' in validated_data:
            profile_data['selfie_photo'] = validated_data.pop('selfie_photo')
        
        # Create user
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            user_type='customer'
        )
        
        # Create profile
        CustomerProfile.objects.create(user=user, **profile_data)
        
        return user


class SalonManagerRegistrationSerializer(serializers.Serializer):
    """Serializer for salon manager registration API."""
    phone_number = serializers.CharField(max_length=11, validators=[validate_iranian_phone])
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    salon_name = serializers.CharField(max_length=100)
    salon_photo = serializers.ImageField(required=False)
    salon_address = serializers.CharField()
    salon_gender_type = serializers.ChoiceField(choices=SalonManagerProfile.SALON_GENDER_CHOICES)
    
    def validate(self, data):
        """Validate password confirmation."""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نیستند")

        if CustomUser.objects.filter(phone_number=data['phone_number']).exists():
             raise serializers.ValidationError({"phone_number": "این شماره تلفن قبلاً ثبت شده است"})

        return data
    
    def create(self, validated_data):
        """Create user and salon manager profile."""
        # Remove password_confirm
        validated_data.pop('password_confirm')
        
        # Extract profile data
        profile_data = {
            'salon_name': validated_data.pop('salon_name'),
            'salon_address': validated_data.pop('salon_address'),
            'salon_gender_type': validated_data.pop('salon_gender_type'),
        }
        
        if 'salon_photo' in validated_data:
            profile_data['salon_photo'] = validated_data.pop('salon_photo')
        
        # Create user
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            user_type='salon_manager'
        )
        
        # Create profile (not approved)
        SalonManagerProfile.objects.create(user=user, is_approved=False, **profile_data)
        
        return user


class StylistProfileCompletionSerializer(serializers.ModelSerializer):
    """Serializer for temporary stylist profile completion."""
    
    class Meta:
        model = StylistProfile
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth']
    
    def update(self, instance, validated_data):
        """Update stylist profile and mark as completed."""
        from django.utils import timezone
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.is_temporary = False
        instance.profile_completed_at = timezone.now()
        instance.save()
        
        return instance
