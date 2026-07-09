import re

from django.core.exceptions import ValidationError


RWANDA_PHONE_DIGIT_PATTERN = re.compile(r'^((?:\+250|250|0)?7\d{8})$')


def normalize_rwandan_phone(phone):
    """Normalize Rwandan phone inputs to +2507XXXXXXXX."""
    if not phone:
        return None

    digits = ''.join(ch for ch in str(phone) if ch.isdigit())
    if digits.startswith('250') and len(digits) == 12 and digits[3] == '7':
        return f'+{digits}'
    if digits.startswith('0') and len(digits) == 10 and digits[1] == '7':
        return f'+250{digits[1:]}'
    if digits.startswith('7') and len(digits) == 9:
        return f'+250{digits}'
    return None


def validate_rwandan_phone(phone):
    normalized = normalize_rwandan_phone(phone)
    if not normalized:
        raise ValidationError(
            'Enter a valid Rwandan phone number in the format +2507XXXXXXXX, 07XXXXXXXX, or 7XXXXXXXX.'
        )
    return normalized
