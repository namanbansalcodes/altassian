from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from user_accounts.permissions import IsAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(ListAPIView):
    """Admin-only endpoint to query the audit trail."""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'user__username']
    search_fields = ['detail', 'resource_id', 'user__username']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']

    def get_queryset(self):
        return AuditLog.objects.select_related('user').all()
