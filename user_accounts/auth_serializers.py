import hashlib
import time

from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import LoginAttempt


class FastTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the standard JWT login serializer to:
    - Include minimal user payload in the login response (avoids /users/me round-trip)
    - Check account lockout before authenticating
    - Record login attempts (success/failure) for security auditing
    """

    username_field = 'username'

    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials. '
                             'Please check your username and password.',
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages.update({
            'required': 'Username is required.',
            'blank': 'Username is required.',
        })
        self.fields['password'].error_messages.update({
            'required': 'Password is required.',
            'blank': 'Password is required.',
        })

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["u"] = user.username
        token["e"] = user.email or ""
        token["r"] = getattr(user, "role", "viewer")
        token["s"] = getattr(user, "status", "pending")
        token["ev"] = user.email_verified
        token["pv"] = getattr(user, "phone_verified", False)
        # Fingerprint: hash of user pk + password hash prefix for revocation on password change
        pw_hash = (user.password or "")[:20]
        token["fp"] = hashlib.sha256(
            f"{user.pk}:{pw_hash}".encode()
        ).hexdigest()[:16]
        token["iat"] = int(time.time())
        return token

    def validate(self, attrs):
        attrs['username'] = attrs.get('username', '').strip()

        if not attrs['username']:
            raise serializers.ValidationError({
                'username': 'Username is required.',
            })

        username = attrs['username']
        request = self.context.get('request')

        # Check account lockout before attempting authentication
        if LoginAttempt.is_locked_out(username):
            LoginAttempt.record(
                username=username, success=False,
                request=request, locked_out=True,
            )
            raise serializers.ValidationError({
                'detail': 'Account temporarily locked due to too many failed login attempts. '
                          'Please try again later.',
            })

        try:
            data = super().validate(attrs)
        except Exception:
            # Record failed attempt
            LoginAttempt.record(
                username=username, success=False, request=request,
            )
            raise

        # Record successful login
        LoginAttempt.record(
            username=username, success=True, request=request,
        )

        u = self.user
        data["user"] = {
            "id": u.pk,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "role": u.role,
            "status": u.status,
            "email_verified": u.email_verified,
            "phone_number": u.phone_number,
            "phone_verified": u.phone_verified,
        }
        return data


class PhoneVerificationSendSerializer(serializers.Serializer):
    """Validates request to send a phone verification code."""
    phone_number = serializers.CharField(
        required=False,
        help_text='Optional: update phone number before sending code.',
    )

    def validate_phone_number(self, value: str) -> str:
        import re
        value = value.strip()
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError(
                'Phone number must be 9-15 digits, optionally prefixed with +.'
            )
        return value


class PhoneVerificationConfirmSerializer(serializers.Serializer):
    """Validates the OTP code submitted for phone verification."""
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        error_messages={
            'required': 'Verification code is required.',
            'blank': 'Verification code is required.',
        },
    )

    def validate_code(self, value: str) -> str:
        if not value.isdigit():
            raise serializers.ValidationError('Verification code must be 6 digits.')
        return value
