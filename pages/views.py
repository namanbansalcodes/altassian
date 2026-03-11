from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Page, PageVersion, Comment, Attachment
from .serializers import (
    PageSerializer, PageVersionSerializer, CommentSerializer,
    AttachmentSerializer, PageTreeSerializer,
)


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.select_related('space', 'created_by', 'updated_by').all()
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['space', 'parent', 'is_draft', 'created_by']
    search_fields = ['title', 'body_markdown']
    ordering_fields = ['title', 'position', 'created_at', 'updated_at']
    ordering = ['-updated_at']

    @action(detail=False, methods=['get'], url_path='tree')
    def tree(self, request: Request) -> Response:
        space_id = request.query_params.get('space')
        if not space_id:
            return Response({'detail': 'space query param is required.'}, status=status.HTTP_400_BAD_REQUEST)
        root_pages = Page.objects.filter(space_id=space_id, parent__isnull=True).order_by('position')
        serializer = PageTreeSerializer(root_pages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='search')
    def full_text_search(self, request: Request) -> Response:
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'detail': 'q query param is required.'}, status=status.HTTP_400_BAD_REQUEST)
        pages = Page.objects.filter(
            Q(title__icontains=q) | Q(body_markdown__icontains=q)
        ).select_related('space', 'created_by')
        page = self.paginate_queryset(pages)
        serializer = PageSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='activity')
    def activity(self, request: Request) -> Response:
        recent = Page.objects.select_related('space', 'created_by', 'updated_by').order_by('-updated_at')
        page = self.paginate_queryset(recent)
        serializer = PageSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class PageVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageVersion.objects.select_related('page', 'edited_by').all()
    serializer_class = PageVersionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['page']
    ordering_fields = ['version_number', 'created_at']
    ordering = ['-version_number']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('page', 'author').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['page', 'author']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.select_related('page', 'uploaded_by').all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['page']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
