from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser, CustomerProfile, StylistProfile, SalonManagerProfile
from apps.salons.models import Salon
from apps.salons.views import manage_stylists

class FixesVerificationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Salon Manager & Salon
        self.manager_user = CustomUser.objects.create_user(phone_number='09120000001', password='password', user_type='salon_manager')
        self.manager_profile = SalonManagerProfile.objects.create(
            user=self.manager_user, 
            salon_name="Test Salon", 
            salon_gender_type='male',
            is_approved=True
        )
        self.salon = Salon.objects.create(
            name="Test Salon", 
            address="Tehran", 
            gender_type='male', 
            manager=self.manager_profile
        )
        
        # Create Male Customer
        self.male_customer = CustomUser.objects.create_user(phone_number='09120000002', password='password', user_type='customer')
        self.male_profile = CustomerProfile.objects.create(
            user=self.male_customer,
            first_name="Ali",
            gender='male',
            date_of_birth='1990-01-01'
        )
        
        # Create Female Customer
        self.female_customer = CustomUser.objects.create_user(phone_number='09120000003', password='password', user_type='customer')
        self.female_profile = CustomerProfile.objects.create(
            user=self.female_customer,
            first_name="Sara",
            gender='female',
            date_of_birth='1990-01-01'
        )
        
        # Create Female Salon
        self.manager_female = CustomUser.objects.create_user(phone_number='09120000004', password='password', user_type='salon_manager')
        self.manager_female_profile = SalonManagerProfile.objects.create(
            user=self.manager_female,
            salon_name="Female Salon",
            salon_gender_type='female',
            is_approved=True
        )
        self.female_salon = Salon.objects.create(
            name="Female Salon",
            address="Tehran",
            gender_type='female',
            manager=self.manager_female_profile
        )

    def test_gender_filtering(self):
        """Test that customers see only their gender salons."""
        # Male reads list
        self.client.force_login(self.male_customer)
        response = self.client.get(reverse('salons:salon_list'))
        self.assertContains(response, "Test Salon")
        self.assertNotContains(response, "Female Salon")
        
        # Female reads list
        self.client.force_login(self.female_customer)
        response = self.client.get(reverse('salons:salon_list'))
        self.assertNotContains(response, "Test Salon")
        self.assertContains(response, "Female Salon")

    def test_stylist_login_flow(self):
        """Test temporary stylist redirect."""
        # Create temporary stylist
        stylist_user = CustomUser.objects.create_user(phone_number='09120000005', password='password', user_type='stylist')
        StylistProfile.objects.create(user=stylist_user, salon=self.salon, is_temporary=True)
        
        self.client.login(phone_number='09120000005', password='password')
        response = self.client.get(reverse('accounts:login'), follow=True) 
        # Note: If login view redirects on POST, we should POST to login
        response = self.client.post(reverse('accounts:login'), {'phone_number': '09120000005', 'password': 'password'})
        self.assertRedirects(response, reverse('accounts:stylist_complete_profile'))

    def test_manager_add_stylist(self):
        """Test manager works with updated view."""
        self.client.force_login(self.manager_user)
        url = reverse('salons:manage_stylists')
        data = {
            'phone_number': '09120000006',
            'first_name': 'New',
            'last_name': 'Stylist',
            'gender': 'male'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302) # Redirects on success
        
        # Verify user created
        self.assertTrue(CustomUser.objects.filter(phone_number='09120000006').exists())
        stylist = CustomUser.objects.get(phone_number='09120000006')
        self.assertTrue(stylist.stylist_profile.is_temporary)

    def test_salon_detail_filtering(self):
        """Test that temporary stylists are hidden in salon detail."""
        salon = self.salon
        # Create active stylist
        active_user = CustomUser.objects.create_user(phone_number='09120000007', password='password', user_type='stylist')
        active_stylist = StylistProfile.objects.create(
            user=active_user, salon=salon, is_temporary=False, first_name="Active", last_name="Stylist"
        )
        # Create temporary stylist
        temp_user = CustomUser.objects.create_user(phone_number='09120000008', password='password', user_type='stylist')
        temp_stylist = StylistProfile.objects.create(
            user=temp_user, salon=salon, is_temporary=True, first_name="Temp", last_name="Stylist"
        )

        response = self.client.get(reverse('salons:salon_detail', args=[salon.id]))
        self.assertContains(response, "Active Stylist")
        self.assertNotContains(response, "Temp Stylist")
        # Check for link
        self.assertContains(response, f"stylist_id={active_stylist.id}")

    def test_booking_prefill(self):
        """Test booking page prefills stylist."""
        salon = self.salon
        active_user = CustomUser.objects.create_user(phone_number='09120000009', password='password', user_type='stylist')
        active_stylist = StylistProfile.objects.create(
            user=active_user, salon=salon, is_temporary=False, first_name="Target", last_name="Stylist"
        )
        self.client.force_login(self.male_customer)
        response = self.client.get(reverse('appointments:booking_page') + f'?stylist_id={active_stylist.id}')
        self.assertContains(response, "Target Stylist")
        self.assertContains(response, "selected")
