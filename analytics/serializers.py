from rest_framework import serializers

from analytics.models import PageView


class TrackPageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = ['id', 'page', 'session_id', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']


class OverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_spaces = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_page_views = serializers.IntegerField()
    new_users_last_7d = serializers.IntegerField()
    new_pages_last_7d = serializers.IntegerField()
    edits_last_7d = serializers.IntegerField()
    views_last_7d = serializers.IntegerField()


class UserActivitySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    pages_created = serializers.IntegerField()
    pages_edited = serializers.IntegerField()
    comments_made = serializers.IntegerField()
    page_views = serializers.IntegerField()


class ContentActivitySerializer(serializers.Serializer):
    page_id = serializers.IntegerField()
    title = serializers.CharField()
    space_key = serializers.CharField()
    view_count = serializers.IntegerField()
    edit_count = serializers.IntegerField()
    comment_count = serializers.IntegerField()


class TimelinePointSerializer(serializers.Serializer):
    date = serializers.DateField()
    views = serializers.IntegerField()
    edits = serializers.IntegerField()
    comments = serializers.IntegerField()
    new_pages = serializers.IntegerField()
