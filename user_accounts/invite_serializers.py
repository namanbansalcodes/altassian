from rest_framework import serializers

from .invite_models import Invite


class InviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ("id", "email", "expires_at", "accepted_at", "created_at")
        read_only_fields = ("id", "expires_at", "accepted_at", "created_at")


class InvitePublicSerializer(serializers.ModelSerializer):
    """What the unauthenticated `/by-token/<t>` GET returns."""

    class Meta:
        model = Invite
        fields = ("email", "expires_at")
        read_only_fields = fields


class InviteAcceptSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(max_length=120)
