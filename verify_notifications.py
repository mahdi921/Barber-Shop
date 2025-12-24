
import os
import sys
import django
from unittest.mock import patch, MagicMock

# Setup Django
sys.path.append('/home/mahdi/Projects/Barber-Shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import CustomUser, CustomerProfile, StylistProfile, SalonManagerProfile
from apps.salons.models import Salon, Service
from apps.appointments.models import Appointment
from apps.chat.services.notifications import send_appointment_created_notification, send_appointment_confirmed_notification

def test_telegram_notifications():
    print("Testing Telegram Notification Logic...")
    
    # Mock data
    customer_user = CustomUser(phone_number='09121111111')
    customer = CustomerProfile(user=customer_user, first_name="Test", last_name="Customer", telegram_chat_id="123456")
    
    salon_manager_user = CustomUser(phone_number='09122222222')
    manager_profile = SalonManagerProfile(user=salon_manager_user, salon_name="Test Salon")
    
    stylist_user = CustomUser(phone_number='09123333333')
    stylist = StylistProfile(user=stylist_user, first_name="Test", last_name="Stylist")
    salon = Salon(name="Barber Shop Pro")
    stylist.salon = salon
    
    service = Service(service_type='haircut', price=150000, duration_minutes=30)
    service.custom_name = "Royal Haircut"
    
    appointment = Appointment(
        id=999,
        customer=customer,
        stylist=stylist,
        service=service,
        status='pending'
    )
    # Mock datetime fields
    from datetime import date, time
    appointment.appointment_date = date(2025, 1, 1)
    appointment.appointment_time = time(10, 0)
    
    # Test Created Notification
    with patch('apps.chat.services.notifications.send_telegram_message') as mock_send:
        mock_send.return_value = True
        print("\n--- Testing Appointment Created ---")
        send_appointment_created_notification(appointment)
        
        if mock_send.called:
            args, _ = mock_send.call_args
            chat_id, message = args
            print(f"SUCCESS: Called send_telegram_message with chat_id={chat_id}")
            print(f"Message Content Preview:\n{message}")
        else:
            print("FAILURE: send_telegram_message was not called")

    # Test Confirmed Notification
    with patch('apps.chat.services.notifications.send_telegram_message') as mock_send:
        mock_send.return_value = True
        print("\n--- Testing Appointment Confirmed ---")
        send_appointment_confirmed_notification(appointment)
        
        if mock_send.called:
            args, _ = mock_send.call_args
            chat_id, message = args
            print(f"SUCCESS: Called send_telegram_message with chat_id={chat_id}")
            print(f"Message Content Preview:\n{message}")
        else:
            print("FAILURE: send_telegram_message was not called")

if __name__ == '__main__':
    test_telegram_notifications()
