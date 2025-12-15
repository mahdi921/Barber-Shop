"""
Iranian phone number validator for authentication.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_iranian_phone(value):
    """
    Validates Iranian phone numbers.
    
    Format: 09XX-XXX-XXXX (with or without dashes)
    Examples: 09123456789, 0912-345-6789
    
    Args:
        value: Phone number string
    
    Raises:
        ValidationError: If format is invalid
    """
    # Remove any dashes or spaces
    phone = value.replace('-', '').replace(' ', '')
    
    # Iranian phone pattern: starts with 09, followed by 9 digits
    pattern = r'^09\d{9}$'
    
    if not re.match(pattern, phone):
        raise ValidationError(
            _('شماره تلفن باید به فرمت 09XXXXXXXXX باشد'),  # Persian: Phone must be 09XXXXXXXXX format
            code='invalid_phone'
        )
    
    return phone
