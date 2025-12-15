from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from apps.accounts.models import CustomUser, SalonManagerProfile, StylistProfile
from apps.salons.models import Salon, Service, WorkingHours
from datetime import time

class SalonModelTests(TestCase):
    def setUp(self):
        # Create user and manager
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password')
        self.manager = SalonManagerProfile.objects.create(
            user=self.user,
            salon_name='Test Salon',
            salon_gender_type='male',
            is_approved=True
        )

    def test_create_salon(self):
        """Test creating a salon linked to a manager."""
        salon = Salon.objects.create(
            manager=self.manager,
            name='My Barbershop',
            address='Test Address',
            gender_type='male'
        )
        self.assertEqual(salon.name, 'My Barbershop')
        self.assertEqual(salon.gender_type, 'male')
        self.assertEqual(salon.average_rating, 0)

    def test_salon_gender_filtering(self):
        """Test custom manager filter for gender."""
        # Male salon (approved)
        s1 = Salon.objects.create(manager=self.manager, name='Male Salon', gender_type='male')
        
        # Female salon (approved)
        user2 = CustomUser.objects.create_user(phone_number='09123456780', password='password')
        manager2 = SalonManagerProfile.objects.create(user=user2, salon_gender_type='female', is_approved=True)
        s2 = Salon.objects.create(manager=manager2, name='Female Salon', gender_type='female')
        
        # Unapproved salon
        user3 = CustomUser.objects.create_user(phone_number='09123456781', password='password')
        manager3 = SalonManagerProfile.objects.create(user=user3, salon_gender_type='male', is_approved=False)
        s3 = Salon.objects.create(manager=manager3, name='Pending Salon', gender_type='male')

        # Test approved() filter
        approved_salons = Salon.objects.approved()
        self.assertIn(s1, approved_salons)
        self.assertIn(s2, approved_salons)
        self.assertNotIn(s3, approved_salons)

        # Test for_gender('male')
        male_salons = Salon.objects.for_gender('male')
        self.assertIn(s1, male_salons)
        self.assertNotIn(s2, male_salons)
        self.assertNotIn(s3, male_salons)

class ServiceModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password')
        self.manager = SalonManagerProfile.objects.create(
            user=self.user, salon_gender_type='male', is_approved=True
        )
        self.salon = Salon.objects.create(manager=self.manager, name='Male Salon', gender_type='male')

    def test_create_valid_service(self):
        service = Service.objects.create(
            salon=self.salon,
            service_type='haircut',
            price=100000,
            duration_minutes=30
        )
        self.assertEqual(service.price, 100000)

    def test_invalid_gender_service(self):
        """Test validation error when adding female service to male salon."""
        service = Service(
            salon=self.salon,
            service_type='nails',  # Female only
            price=150000
        )
        with self.assertRaises(ValidationError):
            service.clean()

class WorkingHoursTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password')
        self.manager = SalonManagerProfile.objects.create(user=self.user, is_approved=True)
        self.salon = Salon.objects.create(manager=self.manager, name='Salon', gender_type='male')

    def test_valid_working_hours(self):
        wh = WorkingHours.objects.create(
            salon=self.salon,
            day_of_week=0,  # Saturday
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        self.assertEqual(wh.day_of_week, 0)

    def test_invalid_time_range(self):
        wh = WorkingHours(
            salon=self.salon,
            day_of_week=1,
            start_time=time(18, 0),
            end_time=time(9, 0)  # End before start
        )
        with self.assertRaises(ValidationError):
            wh.clean()

    def test_either_salon_or_stylist_required(self):
        wh = WorkingHours(
            day_of_week=2,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        with self.assertRaises(ValidationError):
            wh.clean()
