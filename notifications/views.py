from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ListModelMixin, DestroyModelMixin, GenericViewSet):
    """
    list: Return the authenticated user's notifications (newest first).
    destroy: Delete a single notification.
    mark_read: PATCH to mark one notification as read.
    mark_all_read: POST to mark all unread notifications as read.
    unread_count: GET the number of unread notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_read', 'verb', 'target_type']

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
        ).select_related('actor')

    @action(detail=True, methods=['patch'], url_path='read')
    def mark_read(self, request: Request, pk=None) -> Response:
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request: Request) -> Response:
        count = Notification.objects.filter(
            recipient=request.user, is_read=False,
        ).update(is_read=True)
        return Response({'marked_read': count})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request: Request) -> Response:
        count = Notification.objects.filter(
            recipient=request.user, is_read=False,
        ).count()
        return Response({'unread_count': count})
