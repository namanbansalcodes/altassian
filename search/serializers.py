from typing import Any, Dict

from rest_framework import serializers

from pages.models import Page, Comment
from spaces.models import Space


class SearchPageSerializer(serializers.ModelSerializer):
    result_type = serializers.SerializerMethodField()
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    space_name = serializers.ReadOnlyField(source='space.name')
    space_key = serializers.ReadOnlyField(source='space.key')

    class Meta:
        model = Page
        fields = [
            'id', 'result_type', 'title', 'slug', 'space', 'space_name',
            'space_key', 'is_draft', 'created_by', 'created_by_username',
            'created_at', 'updated_at',
        ]

    def get_result_type(self, obj: Page) -> str:
        return 'page'


class SearchSpaceSerializer(serializers.ModelSerializer):
    result_type = serializers.SerializerMethodField()
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Space
        fields = [
            'id', 'result_type', 'name', 'key', 'description',
            'owner', 'owner_username', 'is_archived', 'created_at',
        ]

    def get_result_type(self, obj: Space) -> str:
        return 'space'


class SearchCommentSerializer(serializers.ModelSerializer):
    result_type = serializers.SerializerMethodField()
    author_username = serializers.ReadOnlyField(source='author.username')
    page_title = serializers.ReadOnlyField(source='page.title')
    space_key = serializers.ReadOnlyField(source='page.space.key')

    class Meta:
        model = Comment
        fields = [
            'id', 'result_type', 'body', 'page', 'page_title',
            'space_key', 'author', 'author_username', 'created_at',
        ]

    def get_result_type(self, obj: Comment) -> str:
        return 'comment'


class UnifiedSearchResultSerializer(serializers.Serializer):
    """Wrapper serializer for the unified search response."""
    query = serializers.CharField()
    total_count = serializers.IntegerField()
    pages = SearchPageSerializer(many=True)
    spaces = SearchSpaceSerializer(many=True)
    comments = SearchCommentSerializer(many=True)
