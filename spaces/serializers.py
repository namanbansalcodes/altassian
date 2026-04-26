from rest_framework import serializers

from .models import Space


class SpaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ("id", "slug", "name", "description", "icon", "position", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class SpaceDetailSerializer(SpaceListSerializer):
    pages = serializers.SerializerMethodField()

    class Meta(SpaceListSerializer.Meta):
        fields = SpaceListSerializer.Meta.fields + ("pages",)

    def get_pages(self, obj):
        # Lazy import: pages.serializers.PageTreeNodeSerializer doesn't exist until G4.
        try:
            from pages.serializers import PageTreeNodeSerializer
        except ImportError:
            return []
        try:
            roots = obj.page_set.filter(parent__isnull=True, deleted_at__isnull=True).order_by("position", "id")
            return PageTreeNodeSerializer(roots, many=True).data
        except Exception:
            # Legacy Page model may not have deleted_at — return empty until G2 lands.
            return []
