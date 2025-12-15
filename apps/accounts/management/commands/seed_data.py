"""
Management command to seed the database with sample data.

Usage:
    python manage.py seed_data

This creates:
- Sample customers (male and female)
- Sample salon managers (approved)
- Sample salons (male and female)
- Sample stylists with completed profiles
- Sample services
- Sample working hours
- Sample appointments
- Sample ratings and reviews
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date, time, timedelta

from apps.accounts.models import (
    CustomerProfile, SalonManagerProfile, StylistProfile, SiteAdminProfile
)
from apps.salons.models import Salon, Service, WorkingHours
from apps.appointments.models import Appointment
from apps.ratings.models import Rating, Review

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            User.objects.filter(is_superuser=False).delete()
            Salon.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared'))

        self.stdout.write('Seeding database...')

        # Create fake image
        fake_image = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        # 1. Create site admin
        admin, created = User.objects.get_or_create(
            phone_number='09100000000',
            defaults={
                'user_type': 'site_admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            SiteAdminProfile.objects.create(
                user=admin,
                full_name='مدیر سیستم'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin: {admin.phone_number}'))

        # 2. Create customers
        customers_data = [
            {'phone': '09111111111', 'first': 'علی', 'last': 'محمدی', 'gender': 'male', 'dob': date(1995, 5, 15)},
            {'phone': '09111111112', 'first': 'رضا', 'last': 'احمدی', 'gender': 'male', 'dob': date(1992, 8, 20)},
            {'phone': '09111111113', 'first': 'مریم', 'last': 'کریمی', 'gender': 'female', 'dob': date(1998, 3, 10)},
            {'phone': '09111111114', 'first': 'فاطمه', 'last': 'رضایی', 'gender': 'female', 'dob': date(1996, 11, 5)},
        ]
        
        customers = []
        for data in customers_data:
            user, created = User.objects.get_or_create(
                phone_number=data['phone'],
                defaults={'user_type': 'customer'}
            )
            if created:
                user.set_password('customer123')
                user.save()
                CustomerProfile.objects.create(
                    user=user,
                    first_name=data['first'],
                    last_name=data['last'],
                    selfie_photo=fake_image,
                    gender=data['gender'],
                    date_of_birth=data['dob']
                )
                self.stdout.write(f'  ✓ Customer: {data["first"]} {data["last"]}')
            customers.append(user.customer_profile)

        # 3. Create salon managers and salons
        salons_data = [
            {
                'phone': '09222222221',
                'salon_name': 'سالن مردانه پارس',
                'address': 'تهران، خیابان ولیعصر، پلاک 123',
                'gender': 'male'
            },
            {
                'phone': '09222222222',
                'salon_name': 'سالن زیبایی ستاره',
                'address': 'تهران، خیابان انقلاب، پلاک 456',
                'gender': 'female'
            },
        ]
        
        salons = []
        for data in salons_data:
            manager_user, created = User.objects.get_or_create(
                phone_number=data['phone'],
                defaults={'user_type': 'salon_manager'}
            )
            if created:
                manager_user.set_password('manager123')
                manager_user.save()
                
                manager_profile = SalonManagerProfile.objects.create(
                    user=manager_user,
                    salon_name=data['salon_name'],
                    salon_photo=fake_image,
                    salon_address=data['address'],
                    salon_gender_type=data['gender'],
                    is_approved=True,
                    approved_at=timezone.now(),
                    approved_by=admin
                )
                
                salon = Salon.objects.create(
                    manager=manager_profile,
                    name=data['salon_name'],
                    photo=fake_image,
                    address=data['address'],
                    gender_type=data['gender']
                )
                salons.append(salon)
                self.stdout.write(f'  ✓ Salon: {data["salon_name"]}')

        # 4. Create stylists
        stylists = []
        stylist_counter = 0
        for salon in salons:
            for i in range(2):
                stylist_counter += 1
                # 09 + 30 + 000 + 00 + counter (2 digits)
                phone = f'093000000{stylist_counter:02d}'
                gender = salon.gender_type
                first_name = ['رضا', 'حسین'][i] if gender == 'male' else ['زهرا', 'سارا'][i]
                last_name = ['آرایشگر', 'استایلیست'][i]
                
                stylist_user, created = User.objects.get_or_create(
                    phone_number=phone,
                    defaults={'user_type': 'stylist'}
                )
                if created:
                    stylist_user.set_password('stylist123')
                    stylist_user.save()
                    
                    stylist_profile = StylistProfile.objects.create(
                        user=stylist_user,
                        salon=salon,
                        first_name=first_name,
                        last_name=last_name,
                        gender=gender,
                        date_of_birth=date(1990, 6, 15),
                        is_temporary=False,
                        profile_completed_at=timezone.now()
                    )
                    stylists.append(stylist_profile)
                    self.stdout.write(f'    ✓ Stylist: {first_name} {last_name}')

        # 5. Create services
        for salon in salons:
            if salon.gender_type == 'male':
                services_list = [
                    ('haircut', 'کوتاهی مو', 100000),
                    ('shave', 'اصلاح صورت', 50000),
                    ('beard_trim', 'اصلاح ریش', 70000),
                ]
            else:
                services_list = [
                    ('haircut', 'کوتاهی مو', 150000),
                    ('hair_color', 'رنگ مو', 300000),
                    ('makeup', 'آرایش', 200000),
                    ('nails', 'خدمات ناخن', 80000),
                ]
            
            for service_type, name, price in services_list:
                Service.objects.create(
                    salon=salon,
                    service_type=service_type,
                    custom_name=name,
                    price=price,
                    duration_minutes=60
                )

        # 6. Create working hours
        for salon in salons:
            for day in range(6):  # Saturday to Thursday
                WorkingHours.objects.create(
                    salon=salon,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(18, 0)
                )

        # 7. Create sample appointments
        today = date.today()
        for idx, customer in enumerate(customers[:2]):
            salon = salons[0] if customer.gender == 'male' else salons[1]
            stylist = StylistProfile.objects.filter(salon=salon).first()
            service = Service.objects.filter(salon=salon).first()
            
            if stylist and service:
                appointment = Appointment.objects.create(
                    customer=customer,
                    stylist=stylist,
                    service=service,
                    appointment_date=today + timedelta(days=idx + 1),
                    appointment_time=time(14, 0),
                    status='confirmed'
                )
                self.stdout.write(f'  ✓ Appointment for {customer.full_name}')

        # 8. Create completed appointment with rating
        past_customer = customers[2]
        salon = salons[1]  # Female salon
        stylist = StylistProfile.objects.filter(salon=salon).first()
        service = Service.objects.filter(salon=salon).first()
        
        if stylist and service:
            past_appointment = Appointment.objects.create(
                customer=past_customer,
                stylist=stylist,
                service=service,
                appointment_date=today - timedelta(days=7),
                appointment_time=time(11, 0),
                status='completed'
            )
            
            rating = Rating.objects.create(
                customer=past_customer,
                stylist=stylist,
                appointment=past_appointment,
                rating=5
            )
            
            review = Review.objects.create(
                customer=past_customer,
                stylist=stylist,
                appointment=past_appointment,
                text='عالی بود! خیلی راضی بودم از خدمات.',
                is_approved=True
            )
            
            # Update salon rating cache
            salon.update_rating_cache()
            
            self.stdout.write(f'  ✓ Rating & Review created')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('\nTest Accounts:'))
        self.stdout.write(f'  Admin: 09100000000 / admin123')
        self.stdout.write(f'  Customer (male): 09111111111 / customer123')
        self.stdout.write(f'  Customer (female): 09111111113 / customer123')
        self.stdout.write(f'  Manager: 09222222221 / manager123')
        self.stdout.write(f'  Stylist: 09300000001 / stylist123')
