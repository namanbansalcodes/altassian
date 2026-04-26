from rest_framework import serializers

from .models import CustomUser


class OtpRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class OtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    display_name = serializers.CharField(max_length=120, required=False, allow_blank=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "display_name", "avatar_url", "role", "joined_at")
        read_only_fields = fields
