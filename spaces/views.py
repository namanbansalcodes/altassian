from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Space
from .serializers import SpaceSerializer


class SpaceViewSet(viewsets.ModelViewSet):
    queryset = Space.objects.select_related('owner').all()
    serializer_class = SpaceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_archived', 'owner']
    search_fields = ['name', 'key', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
