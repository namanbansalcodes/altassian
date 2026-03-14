import re
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from rest_framework import serializers


# ── Username ─────────────────────────────────────────────────────────

USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 30
USERNAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9._-]*$')

def validate_username_format(value: str) -> str:
    """Enforce length, charset, and leading-letter rules for usernames."""
    length = len(value)
    if length < USERNAME_MIN_LENGTH:
        raise serializers.ValidationError(
            f'Username must be at least {USERNAME_MIN_LENGTH} characters long.'
        )
    if length > USERNAME_MAX_LENGTH:
        raise serializers.ValidationError(
            f'Username must be {USERNAME_MAX_LENGTH} characters or fewer.'
        )
    if not USERNAME_PATTERN.match(value):
        raise serializers.ValidationError(
            'Username must start with a letter and contain only letters, '
            'numbers, dots, hyphens, or underscores.'
        )
    return value


# ── Email ────────────────────────────────────────────────────────────

EMAIL_MAX_LENGTH = 254  # RFC 5321

def validate_email_format(value: str) -> str:
    """Strict email validation beyond DRF's EmailField."""
    if not value or not value.strip():
        raise serializers.ValidationError('Email address is required.')

    value = value.strip()

    if len(value) > EMAIL_MAX_LENGTH:
        raise serializers.ValidationError(
            f'Email address must be {EMAIL_MAX_LENGTH} characters or fewer.'
        )

    try:
        django_validate_email(value)
    except ValidationError:
        raise serializers.ValidationError(
            'Enter a valid email address (e.g. user@example.com).'
        )

    # Ensure domain has at least one dot (catches user@localhost)
    _local, _, domain = value.rpartition('@')
    if '.' not in domain:
        raise serializers.ValidationError(
            'Enter a valid email address with a proper domain (e.g. user@example.com).'
        )

    return value.lower()


# ── Password ─────────────────────────────────────────────────────────

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

def validate_password_strength(value: str) -> str:
    """
    Enforce password complexity rules on top of Django's built-in validators.
    Requires: length 8-128, at least one uppercase, one lowercase, one digit,
    and one special character.
    """
    if len(value) < PASSWORD_MIN_LENGTH:
        raise serializers.ValidationError(
            f'Password must be at least {PASSWORD_MIN_LENGTH} characters long.'
        )
    if len(value) > PASSWORD_MAX_LENGTH:
        raise serializers.ValidationError(
            f'Password must be {PASSWORD_MAX_LENGTH} characters or fewer.'
        )

    errors: list[str] = []
    if not re.search(r'[A-Z]', value):
        errors.append('at least one uppercase letter')
    if not re.search(r'[a-z]', value):
        errors.append('at least one lowercase letter')
    if not re.search(r'\d', value):
        errors.append('at least one digit')
    if not re.search(r'[^a-zA-Z0-9]', value):
        errors.append('at least one special character (e.g. !@#$%)')

    if errors:
        raise serializers.ValidationError(
            'Password must contain ' + ', '.join(errors) + '.'
        )

    return value


# ── Generic text sanitisation ────────────────────────────────────────

def sanitize_text_input(value: str, field_name: str = 'This field',
                        max_length: int | None = None) -> str:
    """Strip whitespace and enforce optional max-length."""
    value = value.strip()
    if max_length and len(value) > max_length:
        raise serializers.ValidationError(
            f'{field_name} must be {max_length} characters or fewer.'
        )
    return value
