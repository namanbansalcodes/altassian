from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import CustomUserSerializer


class FastTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the standard JWT login serializer to include minimal user payload
    in the login response. This avoids an immediate follow-up /users/me call,
    reducing total auth workflow latency (fewer network round-trips).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add lightweight custom claims for quick client-side needs
        token["u"] = user.username
        token["e"] = user.email or ""
        token["r"] = getattr(user, "role", "viewer")
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Attach a compact user payload to the login response
        data["user"] = CustomUserSerializer(self.user).data
        return data
