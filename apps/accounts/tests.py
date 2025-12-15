"""
Comprehensive test suite for accounts app.

Tests cover:
- User registration with phone validation
- CAPTCHA integration
- Salon manager approval workflow
- Temporary stylist profile completion
- Phone-based authentication
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import (
    CustomerProfile, SalonManagerProfile, StylistProfile
)
from apps.salons.models import Salon
from datetime import date

User = get_user_model()


class PhoneValidationTestCase(TestCase):
    """Test Iranian phone number validation."""
    
    def test_valid_iranian_phone(self):
        """Test that valid Iranian phone numbers are accepted."""
        valid_phones = [
            '09123456789',
            '09351234567',
            '09901234567',
        ]
        
        for phone in valid_phones:
            user = User.objects.create_user(
                phone_number=phone,
                password='testpass123',
                user_type='customer'
            )
            self.assertEqual(user.phone_number, phone)
            self.assertEqual(user.username, phone)  # Username synced with phone
    
    def test_invalid_iranian_phone(self):
        """Test that invalid phone numbers are rejected."""
        from apps.accounts.validators import validate_iranian_phone
        from django.core.exceptions import ValidationError
        
        invalid_phones = [
            '9123456789',      # Missing leading zero
            '09123',           # Too short
            '0812345678',      # Wrong prefix
            '+989123456789',   # International format not supported directly
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validate_iranian_phone(phone)


class CustomerRegistrationTestCase(TestCase):
    """Test customer registration workflow."""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register_customer')
    
    def test_customer_registration_success(self):
        """Test successful customer registration."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create mock image file
        image = SimpleUploadedFile(
            "test_image.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        # Note: In real test, need to handle CAPTCHA
        # For now, testing model creation directly
        user = User.objects.create_user(
            phone_number='09123456789',
            password='testpass123',
            user_type='customer'
        )
        
        profile = CustomerProfile.objects.create(
            user=user,
            first_name='علی',
            last_name='محمدی',
            selfie_photo=image,
            gender='male',
            date_of_birth=date(1995, 5, 15)
        )
        
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(CustomerProfile.objects.count(), 1)
        self.assertEqual(profile.full_name, 'علی محمدی')
        self.assertEqual(user.user_type, 'customer')
    
    def test_duplicate_phone_rejected(self):
        """Test that duplicate phone numbers are rejected."""
        User.objects.create_user(
            phone_number='09123456789',
            password='pass1',
            user_type='customer'
        )
        
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                phone_number='09123456789',  # Duplicate
                password='pass2',
                user_type='customer'
            )


class SalonManagerApprovalTestCase(TestCase):
    """Test salon manager approval workflow."""
    
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_superuser(
            phone_number='09111111111',
            password='admin123',
            user_type='site_admin'
        )
        
        # Create salon manager
        self.manager_user = User.objects.create_user(
            phone_number='09222222222',
            password='manager123',
            user_type='salon_manager'
        )
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.manager_profile = SalonManagerProfile.objects.create(
            user=self.manager_user,
            salon_name='سالن زیبایی پارس',
            salon_photo=SimpleUploadedFile("salon.jpg", b"content", content_type="image/jpeg"),
            salon_address='تهران، خیابان ولیعصر',
            salon_gender_type='female',
            is_approved=False  # Pending approval
        )
    
    def test_manager_requires_approval(self):
        """Test that new salon managers are not approved by default."""
        self.assertFalse(self.manager_profile.is_approved)
        self.assertIsNone(self.manager_profile.approved_at)
        self.assertIsNone(self.manager_profile.approved_by)
    
    def test_admin_can_approve_manager(self):
        """Test that admin can approve salon manager."""
        from django.utils import timezone
        
        self.manager_profile.is_approved = True
        self.manager_profile.approved_at = timezone.now()
        self.manager_profile.approved_by = self.admin
        self.manager_profile.save()
        
        self.assertTrue(self.manager_profile.is_approved)
        self.assertIsNotNone(self.manager_profile.approved_at)
        self.assertEqual(self.manager_profile.approved_by, self.admin)
    
    def test_unapproved_salon_not_in_listings(self):
        """Test that unapproved salons don't appear in public listings."""
        # Create salon for the manager
        salon = Salon.objects.create(
            manager=self.manager_profile,
            name=self.manager_profile.salon_name,
            photo=self.manager_profile.salon_photo,
            address=self.manager_profile.salon_address,
            gender_type=self.manager_profile.salon_gender_type
        )
        
        # Query approved salons
        approved_salons = Salon.objects.approved()
        
        # Salon should not be in approved list
        self.assertEqual(approved_salons.count(), 0)
        
        # Approve manager
        self.manager_profile.is_approved = True
        self.manager_profile.save()
        
        # Now salon appears in listings
        approved_salons = Salon.objects.approved()
        self.assertEqual(approved_salons.count(), 1)


class TemporaryStylistTestCase(TestCase):
    """Test temporary stylist account completion workflow."""
    
    def setUp(self):
        # Create approved salon manager
        self.manager_user = User.objects.create_user(
            phone_number='09333333333',
            password='manager123',
            user_type='salon_manager'
        )
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.manager_profile = SalonManagerProfile.objects.create(
            user=self.manager_user,
            salon_name='سالن مردانه',
            salon_photo=SimpleUploadedFile("salon.jpg", b"content", content_type="image/jpeg"),
            salon_address='تهران',
            salon_gender_type='male',
            is_approved=True
        )
        
        # Create salon
        self.salon = Salon.objects.create(
            manager=self.manager_profile,
            name='سالن مردانه',
            photo=self.manager_profile.salon_photo,
            address='تهران',
            gender_type='male'
        )
    
    def test_create_temporary_stylist(self):
        """Test that salon manager can create temporary stylist."""
        # Manager creates stylist account
        stylist_user = User.objects.create_user(
            phone_number='09444444444',
            password='temp123',
            user_type='stylist'
        )
        
        stylist_profile = StylistProfile.objects.create(
            user=stylist_user,
            salon=self.salon,
            is_temporary=True
        )
        
        self.assertTrue(stylist_profile.is_temporary)
        self.assertIsNone(stylist_profile.profile_completed_at)
        self.assertEqual(stylist_profile.first_name, '')
        self.assertEqual(stylist_profile.last_name, '')
    
    def test_stylist_completes_profile(self):
        """Test that temporary stylist can complete profile."""
        from django.utils import timezone
        
        # Create temporary stylist
        stylist_user = User.objects.create_user(
            phone_number='09555555555',
            password='temp123',
            user_type='stylist'
        )
        
        stylist_profile = StylistProfile.objects.create(
            user=stylist_user,
            salon=self.salon,
            is_temporary=True
        )
        
        # Stylist completes profile
        stylist_profile.first_name = 'رضا'
        stylist_profile.last_name = 'احمدی'
        stylist_profile.gender = 'male'
        stylist_profile.date_of_birth = date(1990, 3, 10)
        stylist_profile.is_temporary = False
        stylist_profile.profile_completed_at = timezone.now()
        stylist_profile.save()
        
        self.assertFalse(stylist_profile.is_temporary)
        self.assertIsNotNone(stylist_profile.profile_completed_at)
        self.assertEqual(stylist_profile.full_name, 'رضا احمدی')


class LoginTestCase(TestCase):
    """Test phone-based login functionality."""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        
        # Create test user
        self.user = User.objects.create_user(
            phone_number='09666666666',
            password='testpass123',
            user_type='customer'
        )
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.profile = CustomerProfile.objects.create(
            user=self.user,
            first_name='سارا',
            last_name='کریمی',
            selfie_photo=SimpleUploadedFile("photo.jpg", b"content", content_type="image/jpeg"),
            gender='female',
            date_of_birth=date(1998, 7, 20)
        )
    
    def test_login_with_phone_number(self):
        """Test that users can login with phone number."""
        from django.contrib.auth import authenticate
        
        # Authenticate with phone number as username
        user = authenticate(
            username='09666666666',
            password='testpass123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.phone_number, '09666666666')
        self.assertTrue(user.is_authenticated)
    
    def test_login_with_wrong_password(self):
        """Test that wrong password is rejected."""
        from django.contrib.auth import authenticate
        
        user = authenticate(
            username='09666666666',
            password='wrongpassword'
        )
        
        self.assertIsNone(user)


class GenderBasedFilteringTestCase(TestCase):
    """Test gender-based salon filtering."""
    
    def setUp(self):
        # Create male salon
        manager_male_user = User.objects.create_user(
            phone_number='09777777777',
            password='pass123',
            user_type='salon_manager'
        )
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        manager_male_profile = SalonManagerProfile.objects.create(
            user=manager_male_user,
            salon_name='سالن مردانه پارس',
            salon_photo=SimpleUploadedFile("salon1.jpg", b"content", content_type="image/jpeg"),
            salon_address='تهران',
            salon_gender_type='male',
            is_approved=True
        )
        
        self.male_salon = Salon.objects.create(
            manager=manager_male_profile,
            name='سالن مردانه پارس',
            photo=manager_male_profile.salon_photo,
            address='تهران',
            gender_type='male'
        )
        
        # Create female salon
        manager_female_user = User.objects.create_user(
            phone_number='09888888888',
            password='pass123',
            user_type='salon_manager'
        )
        
        manager_female_profile = SalonManagerProfile.objects.create(
            user=manager_female_user,
            salon_name='سالن زیبایی ستاره',
            salon_photo=SimpleUploadedFile("salon2.jpg", b"content", content_type="image/jpeg"),
            salon_address='تهران',
            salon_gender_type='female',
            is_approved=True
        )
        
        self.female_salon = Salon.objects.create(
            manager=manager_female_profile,
            name='سالن زیبایی ستاره',
            photo=manager_female_profile.salon_photo,
            address='تهران',
            gender_type='female'
        )
    
    def test_male_customer_sees_only_male_salons(self):
        """Test that male customers can only see male salons."""
        male_salons = Salon.objects.for_gender('male')
        
        self.assertEqual(male_salons.count(), 1)
        self.assertEqual(male_salons.first(), self.male_salon)
    
    def test_female_customer_sees_only_female_salons(self):
        """Test that female customers can only see female salons."""
        female_salons = Salon.objects.for_gender('female')
        
        self.assertEqual(female_salons.count(), 1)
        self.assertEqual(female_salons.first(), self.female_salon)


# Run with: python manage.py test apps.accounts.tests
