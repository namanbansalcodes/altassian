from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', default=None)

    class Meta:
        model = Notification
        fields = [
            'id', 'actor_username', 'verb', 'target_type',
            'target_id', 'message', 'is_read', 'created_at',
        ]
        read_only_fields = fields
