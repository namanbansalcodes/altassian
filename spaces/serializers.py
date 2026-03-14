from typing import Any, Dict

from rest_framework import serializers

from .models import Space


class SpaceSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    page_count = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = ['id', 'name', 'key', 'description', 'owner', 'owner_username', 'page_count', 'created_at', 'is_archived', 'meta_description', 'meta_keywords']
        read_only_fields = ['id', 'owner', 'created_at']

    def get_page_count(self, obj: Space) -> int:
        return obj.page_set.count()

    def create(self, validated_data: Dict[str, Any]) -> Space:
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
