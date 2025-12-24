
import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.append('/home/mahdi/Projects/Barber-Shop')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.serializers import CustomUserSerializer
from apps.accounts.models import CustomUser

def test_serializer():
    # Create a dummy user if not exists (or mock it)
    user = CustomUser(phone_number='09120000000', user_type='customer')
    # We don't save it to avoid DB constraints, just testing serializer
    
    # Mock settings.TELEGRAM_BOT_USERNAME
    # It should be loaded from settings, let's print what it is
    print(f"Settings Bot Username: {settings.TELEGRAM_BOT_USERNAME}")
    
    serializer = CustomUserSerializer(user)
    data = serializer.data
    
    print(f"Serialized Bot Username: {data.get('telegram_bot_username')}")
    
    if data.get('telegram_bot_username') == settings.TELEGRAM_BOT_USERNAME:
        print("SUCCESS: Serializer includes correct bot username.")
    else:
        print("FAILURE: Serializer mismatch.")

if __name__ == '__main__':
    test_serializer()
