"""
SMS provider stub for future integration with Iranian SMS services.
"""
from typing import Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SMSProvider:
    """
    SMS provider interface for sending verification codes and notifications.
    Implement concrete providers for Kavenegar, Ghasedak, etc.
    """
    
    def __init__(self):
        self.api_key = settings.SMS_API_KEY
        self.provider = settings.SMS_PROVIDER
    
    def send_verification_code(self, phone_number: str, code: str) -> bool:
        """
        Send verification code to phone number.
        
        Args:
            phone_number: Iranian phone number (09xxxxxxxxx)
            code: Verification code to send
        
        Returns:
            bool: True if sent successfully
        """
        if self.provider == 'stub':
            # Stub implementation for development
            logger.info(f"[SMS STUB] Sending code {code} to {phone_number}")
            print(f"📱 SMS: Code {code} would be sent to {phone_number}")
            return True
        
        # TODO: Implement actual SMS provider integration
        # elif self.provider == 'kavenegar':
        #     return self._send_via_kavenegar(phone_number, code)
        # elif self.provider == 'ghasedak':
        #     return self._send_via_ghasedak(phone_number, code)
        
        logger.warning(f"Unknown SMS provider: {self.provider}")
        return False
    
    def send_appointment_reminder(self, phone_number: str, appointment_details: dict) -> bool:
        """
        Send appointment reminder to customer.
        
        Args:
            phone_number: Customer phone number
            appointment_details: Dict with appointment info
        
        Returns:
            bool: True if sent successfully
        """
        if self.provider == 'stub':
            logger.info(f"[SMS STUB] Appointment reminder to {phone_number}")
            print(f"📱 SMS: Appointment reminder to {phone_number}")
            return True
        
        return False


# Global SMS provider instance
sms_provider = SMSProvider()
