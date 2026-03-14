from rest_framework import serializers
from integrations.models import APIKey, Webhook, WebhookDelivery


class APIKeySerializer(serializers.ModelSerializer):
    """Read-only serializer for listing API keys (never exposes the full key)."""

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'prefix', 'scope', 'is_active',
            'expires_at', 'last_used_at', 'created_at', 'username',
        ]
        read_only_fields = ['id', 'prefix', 'last_used_at', 'created_at', 'username']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new API key. Returns the raw key only once."""

    raw_key = serializers.CharField(read_only=True)

    class Meta:
        model = APIKey
        fields = ['id', 'name', 'scope', 'expires_at', 'raw_key', 'prefix', 'created_at']
        read_only_fields = ['id', 'raw_key', 'prefix', 'created_at']

    def validate_scope(self, value: str) -> str:
        user = self.context['request'].user
        if value == 'admin' and getattr(user, 'role', None) != 'admin':
            raise serializers.ValidationError('Only admins can create keys with admin scope.')
        return value

    def validate_name(self, value: str) -> str:
        user = self.context['request'].user
        if APIKey.objects.filter(user=user, name=value, is_active=True).exists():
            raise serializers.ValidationError('You already have an active key with this name.')
        return value


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for webhook CRUD."""

    username = serializers.CharField(source='user.username', read_only=True)
    delivery_count = serializers.SerializerMethodField()

    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'secret', 'events', 'is_active',
            'created_at', 'updated_at', 'username', 'delivery_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'username', 'delivery_count']
        extra_kwargs = {
            'secret': {'write_only': True},
        }

    def get_delivery_count(self, obj: Webhook) -> int:
        return obj.deliveries.count()

    def validate_events(self, value: list) -> list:
        valid_events = {choice[0] for choice in Webhook.EVENT_CHOICES}
        for event in value:
            if event not in valid_events:
                raise serializers.ValidationError(
                    f'Invalid event: {event}. Valid events: {sorted(valid_events)}'
                )
        if not value:
            raise serializers.ValidationError('At least one event is required.')
        return value

    def validate_url(self, value: str) -> str:
        if not value.startswith('https://'):
            raise serializers.ValidationError('Webhook URL must use HTTPS.')
        return value


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Read-only serializer for webhook delivery logs."""

    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'event', 'payload', 'status', 'status_code',
            'response_body', 'error_message', 'attempted_at', 'duration_ms',
        ]
        read_only_fields = fields
