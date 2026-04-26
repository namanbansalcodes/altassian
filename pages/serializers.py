from rest_framework import serializers

from .models import Page


class PageTreeNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("id", "slug", "title", "is_draft", "is_public", "position", "children")

    def get_children(self, obj):
        kids = obj.children.filter(deleted_at__isnull=True).order_by("position", "id")
        return PageTreeNodeSerializer(kids, many=True).data


class PageDetailSerializer(serializers.ModelSerializer):
    body_html = serializers.CharField(source="body_html_cache", read_only=True)

    class Meta:
        model = Page
        fields = (
            "id", "space", "parent", "slug", "title", "body_md", "body_html",
            "position", "is_public", "is_draft",
            "created_by", "updated_by", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "slug", "body_html",
            "created_by", "updated_by", "created_at", "updated_at",
        )


class PageMoveSerializer(serializers.Serializer):
    parent_id = serializers.IntegerField(allow_null=True, required=False)
    position = serializers.IntegerField(required=True)
