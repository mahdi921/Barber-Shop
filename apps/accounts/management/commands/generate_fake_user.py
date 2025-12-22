from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser, CustomerProfile
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates a fake customer user for testing'

    def handle(self, *args, **kwargs):
        # Generate random phone suffix
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        phone = f"091{suffix}"
        password = "password123"
        
        user, created = CustomUser.objects.get_or_create(
            phone_number=phone,
            defaults={
                'user_type': 'customer',
                'is_active': True,
                'is_phone_verified': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            
            CustomerProfile.objects.create(
                user=user,
                first_name="کاربر",
                last_name="تست",
                gender="male",
                date_of_birth="2000-01-01"
            )
            
            self.stdout.write(self.style.SUCCESS(f"User created successfully!"))
            self.stdout.write(f"Phone: {phone}")
            self.stdout.write(f"Password: {password}")
        else:
            self.stdout.write(self.style.WARNING(f"User {phone} already exists."))
