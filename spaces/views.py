from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from user_accounts.permissions import IsAdmin

from .models import Space
from .serializers import SpaceDetailSerializer, SpaceListSerializer


class SpaceViewSet(viewsets.ModelViewSet):
    queryset = Space.objects.all()
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SpaceDetailSerializer
        return SpaceListSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
