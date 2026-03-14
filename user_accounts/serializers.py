from typing import Any, Dict

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CustomUser
from .validators import (
    validate_email_format,
    validate_password_strength,
    validate_username_format,
    sanitize_text_input,
)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'bio', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        validators=[validate_password],
        error_messages={
            'blank': 'Password is required.',
            'min_length': 'Password must be at least 8 characters long.',
        },
    )
    password_confirm = serializers.CharField(
        write_only=True,
        error_messages={'blank': 'Password confirmation is required.'},
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email address is required.',
            'blank': 'Email address is required.',
            'invalid': 'Enter a valid email address (e.g. user@example.com).',
        },
    )
    username = serializers.CharField(
        error_messages={
            'required': 'Username is required.',
            'blank': 'Username is required.',
        },
    )
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        error_messages={
            'max_length': 'First name must be 150 characters or fewer.',
        },
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        error_messages={
            'max_length': 'Last name must be 150 characters or fewer.',
        },
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        read_only_fields = ['id']

    def validate_username(self, value: str) -> str:
        value = value.strip()
        validate_username_format(value)
        if CustomUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with this username already exists.')
        return value

    def validate_email(self, value: str) -> str:
        value = validate_email_format(value)
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate_password(self, value: str) -> str:
        validate_password_strength(value)
        return value

    def validate_first_name(self, value: str) -> str:
        return sanitize_text_input(value, 'First name', max_length=150)

    def validate_last_name(self, value: str) -> str:
        return sanitize_text_input(value, 'Last name', max_length=150)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs.get('password') != attrs.get('password_confirm'):
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
        value = validate_email_format(value)
        user = self.context['request'].user
        if CustomUser.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate_first_name(self, value: str) -> str:
        return sanitize_text_input(value, 'First name', max_length=150)

    def validate_last_name(self, value: str) -> str:
        return sanitize_text_input(value, 'Last name', max_length=150)

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
    old_password = serializers.CharField(
        required=True,
        error_messages={'blank': 'Current password is required.'},
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=128,
        validators=[validate_password],
        error_messages={
            'blank': 'New password is required.',
            'min_length': 'Password must be at least 8 characters long.',
        },
    )

    def validate_old_password(self, value: str) -> str:
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate_new_password(self, value: str) -> str:
        validate_password_strength(value)
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Validates the email submitted on the forgotten-password page."""
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email address is required.',
            'blank': 'Email address is required.',
            'invalid': 'Enter a valid email address (e.g. user@example.com).',
        },
    )

    def validate_email(self, value: str) -> str:
        return validate_email_format(value)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Validates the token + new password on the password-reset confirmation page."""
    token = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Reset token is required.',
            'blank': 'Reset token is required.',
        },
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=128,
        validators=[validate_password],
        error_messages={
            'blank': 'New password is required.',
            'min_length': 'Password must be at least 8 characters long.',
        },
    )
    new_password_confirm = serializers.CharField(
        required=True,
        error_messages={
            'blank': 'Password confirmation is required.',
        },
    )

    def validate_new_password(self, value: str) -> str:
        validate_password_strength(value)
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError(
                {'new_password_confirm': 'Passwords do not match.'}
            )
        return attrs
