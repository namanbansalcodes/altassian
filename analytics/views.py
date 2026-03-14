from datetime import timedelta
from typing import Any

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import PageView
from analytics.serializers import (
    ContentActivitySerializer,
    OverviewSerializer,
    TimelinePointSerializer,
    TrackPageViewSerializer,
    UserActivitySerializer,
)
from pages.models import Comment, Page, PageVersion
from spaces.models import Space
from user_accounts.models import CustomUser
from user_accounts.permissions import IsAdmin


class OverviewView(APIView):
    """Dashboard overview with aggregate stats. Admin-only."""
    permission_classes = [IsAdmin]

    def get(self, request: Request) -> Response:
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        data = {
            'total_users': CustomUser.objects.count(),
            'total_spaces': Space.objects.filter(is_archived=False).count(),
            'total_pages': Page.objects.count(),
            'total_comments': Comment.objects.count(),
            'total_page_views': PageView.objects.count(),
            'new_users_last_7d': CustomUser.objects.filter(date_joined__gte=week_ago).count(),
            'new_pages_last_7d': Page.objects.filter(created_at__gte=week_ago).count(),
            'edits_last_7d': PageVersion.objects.filter(created_at__gte=week_ago).count(),
            'views_last_7d': PageView.objects.filter(viewed_at__gte=week_ago).count(),
        }
        serializer = OverviewSerializer(data)
        return Response(serializer.data)


class UserActivityView(APIView):
    """Per-user engagement metrics. Admin-only."""
    permission_classes = [IsAdmin]

    def get(self, request: Request) -> Response:
        days = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)

        users = CustomUser.objects.annotate(
            num_pages_created=Count('pages_created', filter=Q(pages_created__created_at__gte=since)),
            num_pages_edited=Count('pages_updated', filter=Q(pages_updated__updated_at__gte=since)),
            num_comments_made=Count('comment', filter=Q(comment__created_at__gte=since)),
            num_page_views=Count('page_views', filter=Q(page_views__viewed_at__gte=since)),
        ).filter(
            Q(num_pages_created__gt=0) | Q(num_pages_edited__gt=0) |
            Q(num_comments_made__gt=0) | Q(num_page_views__gt=0)
        ).order_by('-num_pages_created', '-num_page_views')[:50]

        results = [
            {
                'user_id': u.id,
                'username': u.username,
                'pages_created': u.num_pages_created,
                'pages_edited': u.num_pages_edited,
                'comments_made': u.num_comments_made,
                'page_views': u.num_page_views,
            }
            for u in users
        ]
        serializer = UserActivitySerializer(results, many=True)
        return Response(serializer.data)


class ContentActivityView(APIView):
    """Most active pages by views, edits, and comments."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        days = int(request.query_params.get('days', 30))
        space_key = request.query_params.get('space_key')
        since = timezone.now() - timedelta(days=days)

        pages = Page.objects.select_related('space').annotate(
            view_count=Count('views', filter=Q(views__viewed_at__gte=since)),
            edit_count=Count('pageversion', filter=Q(pageversion__created_at__gte=since)),
            comment_count=Count('comment', filter=Q(comment__created_at__gte=since)),
        )

        if space_key:
            pages = pages.filter(space__key=space_key)

        pages = pages.order_by('-view_count')[:50]

        results = [
            {
                'page_id': p.id,
                'title': p.title,
                'space_key': p.space.key,
                'view_count': p.view_count,
                'edit_count': p.edit_count,
                'comment_count': p.comment_count,
            }
            for p in pages
        ]
        serializer = ContentActivitySerializer(results, many=True)
        return Response(serializer.data)


class ActivityTimelineView(APIView):
    """Daily activity counts over a date range for charting."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        days = int(request.query_params.get('days', 30))
        now = timezone.now()
        since = now - timedelta(days=days)

        timeline: list[dict[str, Any]] = []
        for i in range(days):
            day_start = (since + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            timeline.append({
                'date': day_start.date(),
                'views': PageView.objects.filter(viewed_at__gte=day_start, viewed_at__lt=day_end).count(),
                'edits': PageVersion.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count(),
                'comments': Comment.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count(),
                'new_pages': Page.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count(),
            })

        serializer = TimelinePointSerializer(timeline, many=True)
        return Response(serializer.data)


class TrackPageViewView(APIView):
    """Record a page view event."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = TrackPageViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
