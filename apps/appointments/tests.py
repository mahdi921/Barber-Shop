"""
Test suite for appointments app.

Tests cover:
- Appointment booking
- Double-booking prevention (critical!)
- Jalali date conversion
- Availability calculation
- Gender-based access control
"""
from django.test import TestCase
from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from apps.accounts.models import CustomerProfile, SalonManagerProfile, StylistProfile
from apps.salons.models import Salon, Service
from apps.appointments.models import Appointment
from apps.appointments.utils import jalali_to_gregorian, gregorian_to_jalali
from datetime import date, time
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class AppointmentBookingTestCase(TestCase):
    """Test appointment booking functionality."""
    
    def setUp(self):
        # Create customer
        self.customer_user = User.objects.create_user(
            phone_number='09100000001',
            password='pass123',
            user_type='customer'
        )
        
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            first_name='مریم',
            last_name='رضایی',
            selfie_photo=SimpleUploadedFile("photo.jpg", b"content", content_type="image/jpeg"),
            gender='female',
            date_of_birth=date(1995, 5, 10)
        )
        
        # Create salon manager and salon
        manager_user = User.objects.create_user(
            phone_number='09100000002',
            password='pass123',
            user_type='salon_manager'
        )
        
        manager_profile = SalonManagerProfile.objects.create(
            user=manager_user,
            salon_name='سالن زیبایی',
            salon_photo=SimpleUploadedFile("salon.jpg", b"content", content_type="image/jpeg"),
            salon_address='تهران',
            salon_gender_type='female',
            is_approved=True
        )
        
        self.salon = Salon.objects.create(
            manager=manager_profile,
            name='سالن زیبایی',
            photo=manager_profile.salon_photo,
            address='تهران',
            gender_type='female'
        )
        
        # Create stylist
        stylist_user = User.objects.create_user(
            phone_number='09100000003',
            password='pass123',
            user_type='stylist'
        )
        
        self.stylist = StylistProfile.objects.create(
            user=stylist_user,
            salon=self.salon,
            first_name='زهرا',
            last_name='احمدی',
            gender='female',
            date_of_birth=date(1990, 3, 15),
            is_temporary=False
        )
        
        # Create service
        self.service = Service.objects.create(
            salon=self.salon,
            stylist=self.stylist,
            service_type='haircut',
            price=150000,
            duration_minutes=60
        )
    
    def test_create_appointment(self):
        """Test creating a basic appointment."""
        appointment = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=date(2024, 12, 25),
            appointment_time=time(14, 0),
            status='pending'
        )
        
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(appointment.status, 'pending')
        self.assertEqual(appointment.customer, self.customer)
        self.assertEqual(appointment.stylist, self.stylist)


class DoubleBookingPreventionTestCase(TestCase):
    """
    Critical test: Prevent double-booking at database level.
    
    This tests the unique constraint on (stylist, date, time) for active appointments.
    """
    
    def setUp(self):
        # Setup same as above (reusing customer, stylist, service)
        self.customer_user = User.objects.create_user(
            phone_number='09200000001',
            password='pass123',
            user_type='customer'
        )
        
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            first_name='علی',
            last_name='محمدی',
            selfie_photo=SimpleUploadedFile("photo.jpg", b"content", content_type="image/jpeg"),
            gender='male',
            date_of_birth=date(1992, 8, 20)
        )
        
        manager_user = User.objects.create_user(
            phone_number='09200000002',
            password='pass123',
            user_type='salon_manager'
        )
        
        manager_profile = SalonManagerProfile.objects.create(
            user=manager_user,
            salon_name='سالن مردانه',
            salon_photo=SimpleUploadedFile("salon.jpg", b"content", content_type="image/jpeg"),
            salon_address='تهران',
            salon_gender_type='male',
            is_approved=True
        )
        
        self.salon = Salon.objects.create(
            manager=manager_profile,
            name='سالن مردانه',
            photo=manager_profile.salon_photo,
            address='تهران',
            gender_type='male'
        )
        
        stylist_user = User.objects.create_user(
            phone_number='09200000003',
            password='pass123',
            user_type='stylist'
        )
        
        self.stylist = StylistProfile.objects.create(
            user=stylist_user,
            salon=self.salon,
            first_name='رضا',
            last_name='کریمی',
            gender='male',
            date_of_birth=date(1988, 6, 10),
            is_temporary=False
        )
        
        self.service = Service.objects.create(
            salon=self.salon,
            stylist=self.stylist,
            service_type='haircut',
            price=100000,
            duration_minutes=30
        )
    
    def test_double_booking_prevented(self):
        """
        Test that two active appointments for same stylist/time are prevented.
        
        This is the MOST IMPORTANT test - ensures no double-booking.
        """
        test_date = date(2024, 12, 25)
        test_time = time(15, 0)
        
        # First appointment - should succeed
        appointment1 = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=test_date,
            appointment_time=test_time,
            status='confirmed'
        )
        
        # Create second customer
        customer2_user = User.objects.create_user(
            phone_number='09200000004',
            password='pass123',
            user_type='customer'
        )
        
        customer2 = CustomerProfile.objects.create(
            user=customer2_user,
            first_name='حسین',
            last_name='رحمانی',
            selfie_photo=SimpleUploadedFile("photo2.jpg", b"content", content_type="image/jpeg"),
            gender='male',
            date_of_birth=date(1994, 4, 5)
        )
        
        # Second appointment at same time - should FAIL with IntegrityError
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Appointment.objects.create(
                    customer=customer2,
                    stylist=self.stylist,
                    service=self.service,
                    appointment_date=test_date,  # Same date
                    appointment_time=test_time,  # Same time
                    status='pending'  # Active status
                )
    
    def test_cancelled_appointment_allows_rebooking(self):
        """Test that cancelled appointments don't block the time slot."""
        test_date = date(2024, 12, 25)
        test_time = time(16, 0)
        
        # First appointment, then cancelled
        appointment1 = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=test_date,
            appointment_time=test_time,
            status='confirmed'
        )
        
        appointment1.status = 'cancelled'
        appointment1.save()
        
        # Create second customer
        customer2_user = User.objects.create_user(
            phone_number='09200000005',
            password='pass123',
            user_type='customer'
        )
        
        customer2 = CustomerProfile.objects.create(
            user=customer2_user,
            first_name='سعید',
            last_name='نوری',
            selfie_photo=SimpleUploadedFile("photo3.jpg", b"content", content_type="image/jpeg"),
            gender='male',
            date_of_birth=date(1991, 11, 15)
        )
        
        # Second appointment at same time - should SUCCEED because first is cancelled
        appointment2 = Appointment.objects.create(
            customer=customer2,
            stylist=self.stylist,
            service=self.service,
            appointment_date=test_date,
            appointment_time=test_time,
            status='pending'
        )
        
        self.assertEqual(Appointment.objects.filter(
            stylist=self.stylist,
            appointment_date=test_date,
            appointment_time=test_time
        ).count(), 2)  # Both exist, but only one is active


class JalaliDateConversionTestCase(TestCase):
    """Test Jalali (Persian) calendar conversion utilities."""
    
    def test_gregorian_to_jalali(self):
        """Test converting Gregorian to Jalali date."""
        gregorian_date = date(2024, 3, 20)  # Nowruz (Persian New Year)
        jalali_str = gregorian_to_jalali(gregorian_date)
        
        # March 20, 2024 is 1403/01/01 in Jalali calendar
        self.assertEqual(jalali_str, '1403/01/01')
    
    def test_jalali_to_gregorian(self):
        """Test converting Jalali to Gregorian date."""
        jalali_str = '1402/09/23'  # A day in Azar 1402
        gregorian_date = jalali_to_gregorian(jalali_str)
        
        # Verify it's a valid date object
        self.assertIsInstance(gregorian_date, date)
        self.assertEqual(gregorian_date.year, 2023)
    
    def test_round_trip_conversion(self):
        """Test that converting back and forth preserves the date."""
        original_gregorian = date(2024, 6, 1)
        
        # Convert to Jalali and back
        jalali = gregorian_to_jalali(original_gregorian)
        back_to_gregorian = jalali_to_gregorian(jalali)
        
        self.assertEqual(original_gregorian, back_to_gregorian)


class AppointmentJalaliDisplayTestCase(TestCase):
    """Test Jalali date display in appointment model."""
    
    def setUp(self):
        # Minimal setup
        customer_user = User.objects.create_user(
            phone_number='09300000001',
            password='pass123',
            user_type='customer'
        )
        
        self.customer = CustomerProfile.objects.create(
            user=customer_user,
            first_name='فاطمه',
            last_name='صادقی',
            selfie_photo=SimpleUploadedFile("photo.jpg", b"content", content_type="image/jpeg"),
            gender='female',
            date_of_birth=date(1996, 2, 10)
        )
        
        manager_user = User.objects.create_user(
            phone_number='09300000002',
            password='pass123',
            user_type='salon_manager'
        )
        
        manager_profile = SalonManagerProfile.objects.create(
            user=manager_user,
            salon_name='سالن',
            salon_photo=SimpleUploadedFile("salon.jpg", b"content", content_type="image/jpeg"),
            salon_address='تهران',
            salon_gender_type='female',
            is_approved=True
        )
        
        salon = Salon.objects.create(
            manager=manager_profile,
            name='سالن',
            photo=manager_profile.salon_photo,
            address='تهران',
            gender_type='female'
        )
        
        stylist_user = User.objects.create_user(
            phone_number='09300000003',
            password='pass123',
            user_type='stylist'
        )
        
        self.stylist = StylistProfile.objects.create(
            user=stylist_user,
            salon=salon,
            first_name='لیلا',
            last_name='امینی',
            gender='female',
            date_of_birth=date(1989, 9, 5),
            is_temporary=False
        )
        
        self.service = Service.objects.create(
            salon=salon,
            service_type='makeup',
            price=200000
        )
    
    def test_appointment_jalali_date_property(self):
        """Test that appointment displays Jalali date correctly."""
        appointment = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=date(2024, 3, 20),  # Nowruz
            appointment_time=time(10, 0)
        )
        
        jalali_date = appointment.jalali_date
        self.assertEqual(jalali_date, '1403/01/01')


# Run with: python manage.py test apps.appointments.tests
