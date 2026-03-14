from typing import Any

from django.db.models import Q, QuerySet
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from pages.models import Page, Comment
from spaces.models import Space
from .serializers import (
    SearchPageSerializer,
    SearchSpaceSerializer,
    SearchCommentSerializer,
)


class UnifiedSearchView(APIView):
    """
    Unified search across pages, spaces, and comments.

    Query params:
        q          – required search term
        type       – filter by result type: page, space, comment (comma-separated)
        space_key  – filter results to a specific space
        status     – filter pages: draft, published, archived
        page       – pagination page number (default 1)
        page_size  – results per type per page (default 20, max 100)
    """
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response(
                {'detail': 'q query param is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result_types = self._parse_types(request.query_params.get('type', ''))
        space_key = request.query_params.get('space_key', '').strip()
        status_filter = request.query_params.get('status', '').strip().lower()
        page = self._parse_int(request.query_params.get('page'), default=1, minimum=1)
        page_size = self._parse_int(request.query_params.get('page_size'), default=20, minimum=1, maximum=100)

        offset = (page - 1) * page_size
        results: dict = {}
        total = 0

        if 'page' in result_types:
            pages_qs = self._search_pages(q, space_key, status_filter)
            page_count = pages_qs.count()
            total += page_count
            page_slice = pages_qs[offset:offset + page_size]
            results['pages'] = SearchPageSerializer(page_slice, many=True).data
            results['pages_count'] = page_count
        else:
            results['pages'] = []
            results['pages_count'] = 0

        if 'space' in result_types:
            spaces_qs = self._search_spaces(q, space_key, status_filter)
            space_count = spaces_qs.count()
            total += space_count
            space_slice = spaces_qs[offset:offset + page_size]
            results['spaces'] = SearchSpaceSerializer(space_slice, many=True).data
            results['spaces_count'] = space_count
        else:
            results['spaces'] = []
            results['spaces_count'] = 0

        if 'comment' in result_types:
            comments_qs = self._search_comments(q, space_key)
            comment_count = comments_qs.count()
            total += comment_count
            comment_slice = comments_qs[offset:offset + page_size]
            results['comments'] = SearchCommentSerializer(comment_slice, many=True).data
            results['comments_count'] = comment_count
        else:
            results['comments'] = []
            results['comments_count'] = 0

        return Response({
            'query': q,
            'page': page,
            'page_size': page_size,
            'total_count': total,
            **results,
        })

    def _parse_types(self, raw: str) -> set:
        valid = {'page', 'space', 'comment'}
        if not raw.strip():
            return valid
        requested = {t.strip().lower() for t in raw.split(',')}
        filtered = requested & valid
        return filtered if filtered else valid

    def _parse_int(self, value: Any, *, default: int, minimum: int = 1, maximum: int = 0) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default
        parsed = max(parsed, minimum)
        if maximum:
            parsed = min(parsed, maximum)
        return parsed

    def _search_pages(self, q: str, space_key: str, status_filter: str) -> QuerySet:
        qs = Page.objects.select_related('space', 'created_by').filter(
            Q(title__icontains=q) | Q(body_markdown__icontains=q)
        )
        if space_key:
            qs = qs.filter(space__key=space_key)
        if status_filter == 'draft':
            qs = qs.filter(is_draft=True)
        elif status_filter == 'published':
            qs = qs.filter(is_draft=False)
        elif status_filter == 'archived':
            qs = qs.filter(space__is_archived=True)
        return qs.order_by('-updated_at')

    def _search_spaces(self, q: str, space_key: str, status_filter: str) -> QuerySet:
        qs = Space.objects.select_related('owner').filter(
            Q(name__icontains=q) | Q(key__icontains=q) | Q(description__icontains=q)
        )
        if space_key:
            qs = qs.filter(key=space_key)
        if status_filter == 'archived':
            qs = qs.filter(is_archived=True)
        elif status_filter in ('published', 'draft'):
            qs = qs.filter(is_archived=False)
        return qs.order_by('-created_at')

    def _search_comments(self, q: str, space_key: str) -> QuerySet:
        qs = Comment.objects.select_related('page', 'page__space', 'author').filter(
            Q(body__icontains=q)
        )
        if space_key:
            qs = qs.filter(page__space__key=space_key)
        return qs.order_by('-created_at')
