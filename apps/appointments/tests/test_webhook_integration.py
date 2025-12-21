"""
Comprehensive tests for Make.com webhook integration.
"""
import json
from unittest.mock import patch, Mock
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from datetime import datetime, time, timedelta
import responses

from apps.appointments.models import Appointment, WebhookDelivery
from apps.appointments.tasks import (
    build_webhook_payload,
    compute_signature,
    exponential_backoff,
    deliver_appointment_webhook,
    mask_phone
)
from apps.accounts.models import CustomUser, CustomerProfile, StylistProfile, SalonManagerProfile
from apps.salons.models import Salon, Service


class WebhookPayloadTestCase(TestCase):
    """Test webhook payload generation."""
    
    def setUp(self):
        """Create test data."""
        # Create customer
        self.customer_user = CustomUser.objects.create_user(
            phone_number='09121234567',
            user_type='customer'
        )
        self.customer = CustomerProfile.objects.create(
            user=self.customer_user,
            first_name='علی',
            last_name='محمدی',
            gender='male',
            date_of_birth='1990-01-01'
        )
        
        # Create salon manager
        manager_user = CustomUser.objects.create_user(
            phone_number='09127654321',
            user_type='salon_manager'
        )
        self.manager = SalonManagerProfile.objects.create(
            user=manager_user,
            salon_name='آرایشگاه تست',
            salon_address='تهران',
            salon_gender_type='male',
            is_approved=True
        )
        
        # Create salon
        self.salon = Salon.objects.create(
            manager=self.manager,
            name='آرایشگاه تست',
            photo='test.jpg',
            address='تهران، خیابان ولیعصر',
            gender_type='male'
        )
        
        # Create stylist
        stylist_user = CustomUser.objects.create_user(
            phone_number='09129876543',
            user_type='stylist'
        )
        self.stylist = StylistProfile.objects.create(
            user=stylist_user,
            salon=self.salon,
            first_name='رضا',
            last_name='احمدی',
            gender='male',
            is_temporary=False
        )
        
        # Create service
        self.service = Service.objects.create(
            salon=self.salon,
            service_type='haircut',
            custom_name='کوتاهی مو مردانه',
            price=150000,
            duration_minutes=30
        )
        
        # Create appointment
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=datetime(2025, 12, 22).date(),
            appointment_time=time(14, 0),
            status='pending'
        )
    
    def test_build_webhook_payload_structure(self):
        """Test webhook payload has correct structure."""
        payload = build_webhook_payload(self.appointment, 'created')
        
        # Check top-level keys
        self.assertIn('appointment_id', payload)
        self.assertIn('event_type', payload)
        self.assertIn('created_at', payload)
        self.assertIn('customer', payload)
        self.assertIn('salon', payload)
        self.assertIn('stylist', payload)
        self.assertIn('services', payload)
        self.assertIn('total_price', payload)
        self.assertIn('total_duration_minutes', payload)
        self.assertIn('appointment_start', payload)
        self.assertIn('appointment_end', payload)
        self.assertIn('metadata', payload)
        
        # Check customer structure
        self.assertEqual(payload['customer']['first_name'], 'علی')
        self.assertEqual(payload['customer']['last_name'], 'محمدی')
        
        # Check phone masking
        self.assertIn('***', payload['customer']['phone'])
        
        # Check salon
        self.assertEqual(payload['salon']['name'], 'آرایشگاه تست')
        
        # Check stylist
        self.assertEqual(payload['stylist']['name'], 'رضا احمدی')
        
        # Check services array
        self.assertEqual(len(payload['services']), 1)
        self.assertEqual(payload['services'][0]['name'], 'کوتاهی مو مردانه')
        
        # Check totals
        self.assertEqual(payload['total_price'], '150000')
        self.assertEqual(payload['total_duration_minutes'], 30)
    
    def test_event_type_in_payload(self):
        """Test event type is included in payload."""
        created_payload = build_webhook_payload(self.appointment, 'created')
        self.assertEqual(created_payload['event_type'], 'created')
        
        confirmed_payload = build_webhook_payload(self.appointment, 'confirmed')
        self.assertEqual(confirmed_payload['event_type'], 'confirmed')


class WebhookSecurityTestCase(TestCase):
    """Test webhook security features."""
    
    def test_compute_signature(self):
        """Test HMAC signature generation."""
        body = '{"test": "data"}'
        secret = 'my-secret-key'
        
        signature = compute_signature(body, secret)
        
        # Signature should be a hex string
        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 64)  # SHA256 hex is 64 chars
        
        # Same input should produce same signature
        signature2 = compute_signature(body, secret)
        self.assertEqual(signature, signature2)
        
        # Different secret should produce different signature
        signature3 = compute_signature(body, 'different-secret')
        self.assertNotEqual(signature, signature3)
    
    def test_mask_phone(self):
        """Test phone number masking."""
        self.assertEqual(mask_phone('09121234567'), '0912***4567')
        self.assertEqual(mask_phone('09187654321'), '0918***4321')
        
        # Short numbers should not crash
        self.assertEqual(mask_phone('123'), '123')
        self.assertEqual(mask_phone(''), '')


class WebhookRetryTestCase(TestCase):
    """Test webhook retry logic."""
    
    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        # No retries = base delay
        delay0 = exponential_backoff(0, base_delay=60, jitter=False)
        self.assertEqual(delay0, 60)
        
        # 1 retry = 2x base delay
        delay1 = exponential_backoff(1, base_delay=60, jitter=False)
        self.assertEqual(delay1, 120)
        
        # 2 retries = 4x base delay
        delay2 = exponential_backoff(2, base_delay=60, jitter=False)
        self.assertEqual(delay2, 240)
        
        # Should not exceed max_delay
        delay_high = exponential_backoff(20, base_delay=60, max_delay=3600, jitter=False)
        self.assertEqual(delay_high, 3600)
        
        # With jitter, result should be in range
        delay_jitter = exponential_backoff(1, base_delay=60, jitter=True)
        self.assertGreaterEqual(delay_jitter, 60)
        self.assertLessEqual(delay_jitter, 120)


class WebhookSignalTestCase(TransactionTestCase):
    """Test webhook signal triggering."""
    
    def setUp(self):
        """Create test data."""
        customer_user = CustomUser.objects.create_user(
            phone_number='09121234567',
            user_type='customer'
        )
        self.customer = CustomerProfile.objects.create(
            user=customer_user,
            first_name='علی',
            last_name='محمدی',
            gender='male',
            date_of_birth='1990-01-01'
        )
        
        manager_user = CustomUser.objects.create_user(
            phone_number='09127654321',
            user_type='salon_manager'
        )
        manager = SalonManagerProfile.objects.create(
            user=manager_user,
            salon_name='آرایشگاه تست',
            salon_address='تهران',
            salon_gender_type='male',
            is_approved=True
        )
        
        salon = Salon.objects.create(
            manager=manager,
            name='آرایشگاه تست',
            photo='test.jpg',
            address='تهران',
            gender_type='male'
        )
        
        stylist_user = CustomUser.objects.create_user(
            phone_number='09129876543',
            user_type='stylist'
        )
        self.stylist = StylistProfile.objects.create(
            user=stylist_user,
            salon=salon,
            first_name='رضا',
            last_name='احمدی',
            gender='male',
            is_temporary=False
        )
        
        self.service = Service.objects.create(
            salon=salon,
            service_type='haircut',
            custom_name='کوتاهی مو',
            price=150000,
            duration_minutes=30
        )
    
    @patch('apps.appointments.signals.deliver_appointment_webhook.delay')
    def test_appointment_created_triggers_webhook(self, mock_delay):
        """Test that creating an appointment triggers webhook."""
        appointment = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=datetime(2025, 12, 22).date(),
            appointment_time=time(14, 0),
            status='pending'
        )
        
        # Should trigger 'created' webhook
        mock_delay.assert_called_once_with(str(appointment.id), 'created')
    
    @patch('apps.appointments.signals.deliver_appointment_webhook.delay')
    def test_appointment_confirmed_triggers_webhook(self, mock_delay):
        """Test that confirming an appointment triggers webhook."""
        appointment = Appointment.objects.create(
            customer=self.customer,
            stylist=self.stylist,
            service=self.service,
            appointment_date=datetime(2025, 12, 22).date(),
            appointment_time=time(14, 0),
            status='pending'
        )
        
        # Clear the call from creation
        mock_delay.reset_mock()
        
        # Confirm the appointment
        appointment.status = 'confirmed'
        appointment.save()
        
        # Should trigger 'confirmed' webhook
        mock_delay.assert_called_once_with(str(appointment.id), 'confirmed')


class WebhookDeliveryTestCase(TransactionTestCase):
    """Test webhook delivery task with mocked HTTP."""
    
    def setUp(self):
        """Create test data."""
        customer_user = CustomUser.objects.create_user(
            phone_number='09121234567',
            user_type='customer'
        )
        customer = CustomerProfile.objects.create(
            user=customer_user,
            first_name='علی',
            last_name='محمدی',
            gender='male',
            date_of_birth='1990-01-01'
        )
        
        manager_user = CustomUser.objects.create_user(
            phone_number='09127654321',
            user_type='salon_manager'
        )
        manager = SalonManagerProfile.objects.create(
            user=manager_user,
            salon_name='آرایشگاه تست',
            salon_address='تهران',
            salon_gender_type='male',
            is_approved=True
        )
        
        salon = Salon.objects.create(
            manager=manager,
            name='آرایشگاه تست',
            photo='test.jpg',
            address='تهران',
            gender_type='male'
        )
        
        stylist_user = CustomUser.objects.create_user(
            phone_number='09129876543',
            user_type='stylist'
        )
        stylist = StylistProfile.objects.create(
            user=stylist_user,
            salon=salon,
            first_name='رضا',
            last_name='احمدی',
            gender='male',
            is_temporary=False
        )
        
        service = Service.objects.create(
            salon=salon,
            service_type='haircut',
            custom_name='کوتاهی مو',
            price=150000,
            duration_minutes=30
        )
        
        self.appointment = Appointment.objects.create(
            customer=customer,
            stylist=stylist,
            service=service,
            appointment_date=datetime(2025, 12, 22).date(),
            appointment_time=time(14, 0),
            status='pending'
        )
    
    @responses.activate
    @patch('apps.appointments.tasks.settings.MAKE_WEBHOOK_URL', 'https://hook.make.com/test')
    @patch('apps.appointments.tasks.settings.MAKE_WEBHOOK_SECRET', 'test-secret')
    def test_successful_webhook_delivery(self):
        """Test successful webhook delivery creates proper records."""
        # Mock successful response
        responses.add(
            responses.POST,
            'https://hook.make.com/test',
            json={'success': True},
            status=200
        )
        
        # Call task synchronously
        deliver_appointment_webhook(str(self.appointment.id), 'created')
        
        # Check delivery record created
        delivery = WebhookDelivery.objects.get(
            appointment=self.appointment,
            event_type='created'
        )
        
        self.assertEqual(delivery.status, 'sent')
        self.assertEqual(delivery.response_code, 200)
        self.assertEqual(delivery.attempts_count, 1)
        
        # Check appointment marked as sent
        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.webhook_created_sent)

    
    @patch('apps.appointments.tasks.settings.MAKE_WEBHOOK_URL', '')
    def test_no_webhook_url_stores_pending(self):
        """Test that missing webhook URL stores delivery as pending."""
        deliver_appointment_webhook(str(self.appointment.id), 'created')
        
        delivery = WebhookDelivery.objects.get(
            appointment=self.appointment,
            event_type='created'
        )
        
        self.assertEqual(delivery.status, 'pending')
        self.assertIn('No webhook URL configured', delivery.error_message)
    
    @responses.activate
    @patch('apps.appointments.tasks.settings.MAKE_WEBHOOK_URL', 'https://hook.make.com/test')
    @patch('apps.appointments.tasks.settings.MAKE_WEBHOOK_SECRET', 'test-secret')
    def test_idempotency_key_format(self):
        """Test idempotency key has correct format."""
        responses.add(
            responses.POST,
            'https://hook.make.com/test',
            json={'success': True},
            status=200
        )
        
        deliver_appointment_webhook(str(self.appointment.id), 'created')
        
        delivery = WebhookDelivery.objects.get(
            appointment=self.appointment,
            event_type='created'
        )
        
        expected_key = f"appointment:{self.appointment.id}:created"
        self.assertEqual(delivery.idempotency_key, expected_key)
