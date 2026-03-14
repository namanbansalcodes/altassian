from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class FastTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the standard JWT login serializer to include minimal user payload
    in the login response. This avoids an immediate follow-up /users/me call,
    reducing total auth workflow latency (fewer network round-trips).

    Adds input validation for the login form:
    - username: required, stripped of whitespace
    - password: required, not blank
    """

    username_field = 'username'

    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials. '
                             'Please check your username and password.',
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Override field error messages for clearer login-page feedback
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
        # Strip whitespace from username before authentication
        attrs['username'] = attrs.get('username', '').strip()

        if not attrs['username']:
            raise serializers.ValidationError({
                'username': 'Username is required.',
            })

        data = super().validate(attrs)
        u = self.user
        data["user"] = {
            "id": u.pk,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "role": u.role,
        }
        return data
