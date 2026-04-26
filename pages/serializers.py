from rest_framework import serializers

from .models import Attachment, Comment, Page, PageVersion


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

    def validate_is_public(self, value):
        request = self.context.get("request")
        instance = self.instance
        # Only admins may flip is_public on or off.
        was_public = bool(instance.is_public) if instance else False
        if value != was_public and not (request and request.user.is_authenticated and request.user.is_admin):
            raise serializers.ValidationError("Only admins can change page visibility.")
        return value


class PageMoveSerializer(serializers.Serializer):
    parent_id = serializers.IntegerField(allow_null=True, required=False)
    position = serializers.IntegerField(required=True)


class PageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageVersion
        fields = ("id", "version_n", "body_md", "edited_by", "change_summary", "created_at")
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "page", "author", "body_md", "parent", "created_at", "deleted_at")
        read_only_fields = ("id", "author", "created_at", "deleted_at")


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ("id", "page", "file_url", "original_filename", "mime_type", "size_bytes", "uploaded_by", "created_at")
        read_only_fields = ("id", "page", "file_url", "uploaded_by", "created_at", "original_filename", "mime_type", "size_bytes")

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else ""
