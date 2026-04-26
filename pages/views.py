from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Page
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import PageDetailSerializer, PageMoveSerializer


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
