from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', default='anonymous')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'username', 'action', 'resource_type',
            'resource_id', 'detail', 'ip_address', 'timestamp',
        ]
        read_only_fields = fields
