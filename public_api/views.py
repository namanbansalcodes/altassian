from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from pages.models import Page


class PublicPageView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def get(self, request, space_slug, page_slug):
        page = get_object_or_404(
            Page,
            space__slug=space_slug,
            slug=page_slug,
            is_public=True,
            deleted_at__isnull=True,
        )
        return Response({
            "title": page.title,
            "body_md": page.body_md,
            "body_html": page.body_html_cache,
            "updated_at": page.updated_at,
        })
