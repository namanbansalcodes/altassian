from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Attachment, Comment, Page, PageVersion
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    AttachmentSerializer,
    CommentSerializer,
    PageDetailSerializer,
    PageMoveSerializer,
    PageVersionSerializer,
)


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.filter(deleted_at__isnull=True)
    serializer_class = PageDetailSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrAdminOrReadOnly)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        instance.refresh_from_db()
        serializer.instance = instance

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        page = self.get_object()
        page.deleted_at = timezone.now()
        page.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="move")
    def move(self, request, pk=None):
        page = self.get_object()
        s = PageMoveSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        parent_id = s.validated_data.get("parent_id")
        if parent_id is not None:
            parent = get_object_or_404(Page, pk=parent_id, space=page.space, deleted_at__isnull=True)
            if parent.pk == page.pk:
                return Response({"detail": "A page cannot be its own parent."}, status=400)
            page.parent = parent
        else:
            page.parent = None
        page.position = s.validated_data["position"]
        page.updated_by = request.user
        page.save(update_fields=["parent", "position", "updated_by", "updated_at"])
        return Response(PageDetailSerializer(page).data)

    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        page = self.get_object()
        qs = page.versions.order_by("version_n")
        return Response(PageVersionSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"], url_path=r"versions/(?P<version_n>\d+)")
    def version_detail(self, request, pk=None, version_n=None):
        page = self.get_object()
        v = get_object_or_404(PageVersion, page=page, version_n=int(version_n))
        return Response(PageVersionSerializer(v).data)

    @action(detail=True, methods=["post"], url_path=r"restore/(?P<version_n>\d+)")
    def restore(self, request, pk=None, version_n=None):
        page = self.get_object()
        v = get_object_or_404(PageVersion, page=page, version_n=int(version_n))
        page.body_md = v.body_md
        page.updated_by = request.user
        page.save()  # signal creates a new PageVersion
        return Response(PageDetailSerializer(page).data)


class CommentListCreateView(viewsets.GenericViewSet):
    """Custom small viewset for the nested page → comments route."""
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def list(self, request, page_pk=None):
        qs = Comment.objects.filter(page_id=page_pk, deleted_at__isnull=True).select_related("author")
        return Response(CommentSerializer(qs, many=True).data)

    def create(self, request, page_pk=None):
        page = get_object_or_404(Page, pk=page_pk, deleted_at__isnull=True)
        s = CommentSerializer(data={**request.data, "page": page.id})
        s.is_valid(raise_exception=True)
        s.save(author=request.user, page=page)
        return Response(s.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def destroy(self, request, pk=None):
        c = get_object_or_404(Comment, pk=pk, deleted_at__isnull=True)
        if not (request.user.is_admin or c.author_id == request.user.id):
            raise PermissionDenied()
        c.deleted_at = timezone.now()
        c.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AttachmentUploadView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttachmentSerializer

    def create(self, request, page_pk=None):
        page = get_object_or_404(Page, pk=page_pk, deleted_at__isnull=True)
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "No file uploaded."}, status=400)
        att = Attachment.objects.create(
            page=page,
            file=f,
            original_filename=f.name,
            mime_type=f.content_type or "application/octet-stream",
            size_bytes=f.size,
            uploaded_by=request.user,
        )
        return Response(
            AttachmentSerializer(att, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AttachmentDeleteView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttachmentSerializer

    def destroy(self, request, pk=None):
        a = get_object_or_404(Attachment, pk=pk)
        if not (request.user.is_admin or a.uploaded_by_id == request.user.id):
            raise PermissionDenied()
        a.file.delete(save=False)
        a.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
