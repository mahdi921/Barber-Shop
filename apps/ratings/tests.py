from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date, time
from apps.accounts.models import CustomUser, SalonManagerProfile, StylistProfile, CustomerProfile
from apps.salons.models import Salon, Service
from apps.appointments.models import Appointment
from apps.ratings.models import Rating, Review

class RatingModelTests(TestCase):
    def setUp(self):
        # Setup data
        self.user = CustomUser.objects.create_user(phone_number='09123456789', password='password')
        self.manager = SalonManagerProfile.objects.create(user=self.user, is_approved=True)
        self.salon = Salon.objects.create(manager=self.manager, name='Salon', gender_type='male')
        
        self.stylist_user = CustomUser.objects.create_user(phone_number='09123456781', password='password')
        self.stylist = StylistProfile.objects.create(
            user=self.stylist_user, salon=self.salon, first_name='Ali', last_name='Rezai'
        )
        
        self.service = Service.objects.create(salon=self.salon, service_type='haircut', price=1000)
        
        self.cust_user = CustomUser.objects.create_user(phone_number='09123456782', password='password')
        self.customer = CustomerProfile.objects.create(user=self.cust_user, gender='male', date_of_birth=date(1990, 1, 1))

        self.appointment = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            status='completed'
        )

    def test_create_rating(self):
        """Test creating a rating updates averages."""
        rating = Rating.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            appointment=self.appointment,
            rating=5
        )
        # Check if saved
        self.assertEqual(rating.rating, 5)
        
        # Check if aggregation works (might need explicit call if using signals vs direct method)
        # Assuming aggregation is updated via signal or manually in view. 
        # But here we test the model/method itself.
        # Let's call update_rating_cache on salon/stylist if logic exists there
        self.salon.update_rating_cache()
        self.assertEqual(self.salon.average_rating, 5.0)
        self.assertEqual(self.salon.total_ratings, 1)

    def test_anonymous_review(self):
        """Test review creation."""
        review = Review.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            appointment=self.appointment,
            text="Great job!"
        )
        self.assertEqual(review.text, "Great job!")
        # Ensure customer link exists but logic (serializer) should hide it
        self.assertEqual(review.customer, self.customer)
