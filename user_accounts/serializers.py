from typing import Any, Dict

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'bio', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        read_only_fields = ['id']

    def validate_email(self, value: str) -> str:
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar']

    def validate_email(self, value: str) -> str:
        user = self.context['request'].user
        normalized = value.lower()
        if CustomUser.objects.filter(email__iexact=normalized).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return normalized

    def validate_first_name(self, value: str) -> str:
        if value and len(value) > 150:
            raise serializers.ValidationError('First name must be 150 characters or fewer.')
        return value

    def validate_last_name(self, value: str) -> str:
        if value and len(value) > 150:
            raise serializers.ValidationError('Last name must be 150 characters or fewer.')
        return value

    def validate_bio(self, value: str) -> str:
        if value and len(value) > 2000:
            raise serializers.ValidationError('Bio must be 2000 characters or fewer.')
        return value


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['role']

    def validate_role(self, value: str) -> str:
        valid_roles = [choice[0] for choice in CustomUser._meta.get_field('role').choices]
        if value not in valid_roles:
            raise serializers.ValidationError(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value: str) -> str:
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
