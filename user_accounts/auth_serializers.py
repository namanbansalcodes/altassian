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
            "email_verified": u.email_verified,
        }
        return data
