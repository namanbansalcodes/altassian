from typing import Any, Dict, List

from rest_framework import serializers

from .models import Page, PageVersion, Comment, Attachment


class PageVersionSerializer(serializers.ModelSerializer):
    edited_by_username = serializers.ReadOnlyField(source='edited_by.username')

    class Meta:
        model = PageVersion
        fields = ['id', 'page', 'version_number', 'body_markdown', 'edited_by', 'edited_by_username', 'created_at', 'change_summary']
        read_only_fields = ['id', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'page', 'author', 'author_username', 'body', 'parent', 'replies', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def get_replies(self, obj: Comment) -> List[Dict[str, Any]]:
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

    def create(self, validated_data: Dict[str, Any]) -> Comment:
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class AttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')

    class Meta:
        model = Attachment
        fields = ['id', 'page', 'file', 'uploaded_by', 'uploaded_by_username', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at']

    def create(self, validated_data: Dict[str, Any]) -> Attachment:
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class PageSerializer(serializers.ModelSerializer):
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    updated_by_username = serializers.ReadOnlyField(source='updated_by.username')
    space_name = serializers.ReadOnlyField(source='space.name')

    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'space', 'space_name', 'parent', 'body_markdown', 'body_html',
            'created_by', 'created_by_username', 'updated_by', 'updated_by_username',
            'position', 'is_draft', 'created_at', 'updated_at',
            'meta_description', 'meta_keywords', 'og_image', 'canonical_url', 'noindex',
        ]
        read_only_fields = ['id', 'slug', 'created_by', 'updated_by', 'created_at', 'updated_at']

    def create(self, validated_data: Dict[str, Any]) -> Page:
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['updated_by'] = user
        return super().create(validated_data)

    def update(self, instance: Page, validated_data: Dict[str, Any]) -> Page:
        user = self.context['request'].user
        validated_data['updated_by'] = user
        # Auto-create a PageVersion before updating
        last_version = PageVersion.objects.filter(page=instance).order_by('-version_number').first()
        next_version = (last_version.version_number + 1) if last_version else 1
        PageVersion.objects.create(
            page=instance,
            version_number=next_version,
            body_markdown=instance.body_markdown,
            edited_by=user,
            change_summary=self.context['request'].data.get('change_summary', ''),
        )
        return super().update(instance, validated_data)


class PageTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'position', 'is_draft', 'children']

    def get_children(self, obj: Page) -> List[Dict[str, Any]]:
        children = Page.objects.filter(parent=obj).order_by('position')
        return PageTreeSerializer(children, many=True).data
