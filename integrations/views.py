import hashlib
import hmac
import json
import logging
import time
from urllib.request import urlopen, Request as URLRequest
from urllib.error import URLError

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from integrations.models import APIKey, Webhook, WebhookDelivery, generate_api_key, hash_api_key
from integrations.serializers import (
    APIKeySerializer, APIKeyCreateSerializer,
    WebhookSerializer, WebhookDeliverySerializer,
)

logger = logging.getLogger('altassian')


class APIKeyViewSet(viewsets.ModelViewSet):
    """Manage personal API keys for programmatic access."""

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'admin':
            return APIKey.objects.select_related('user').all()
        return APIKey.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeySerializer

    def perform_create(self, serializer: APIKeyCreateSerializer) -> None:
        raw_key = generate_api_key()
        hashed = hash_api_key(raw_key)
        prefix = raw_key[:12]
        instance = serializer.save(
            user=self.request.user,
            hashed_key=hashed,
            prefix=prefix,
        )
        instance.raw_key = raw_key

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        data = APIKeyCreateSerializer(instance, context={'request': request}).data
        data['raw_key'] = instance.raw_key
        logger.info('API key created: %s by user %s', instance.prefix, request.user.username)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def revoke(self, request: Request, pk: str = None) -> Response:
        """Deactivate an API key."""
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save(update_fields=['is_active'])
        logger.info('API key revoked: %s by user %s', api_key.prefix, request.user.username)
        return Response({'detail': 'API key revoked.'})

    @action(detail=False, methods=['get'])
    def active(self, request: Request) -> Response:
        """List only active, non-expired keys for the current user."""
        qs = APIKey.objects.filter(user=request.user, is_active=True).exclude(
            expires_at__lt=timezone.now()
        )
        serializer = APIKeySerializer(qs, many=True)
        return Response(serializer.data)


class WebhookViewSet(viewsets.ModelViewSet):
    """Manage webhook subscriptions for event notifications."""

    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'admin':
            return Webhook.objects.select_related('user').all()
        return Webhook.objects.filter(user=user)

    def perform_create(self, serializer: WebhookSerializer) -> None:
        serializer.save(user=self.request.user)
        logger.info('Webhook created: %s by user %s', serializer.instance.name, self.request.user.username)

    @action(detail=True, methods=['post'])
    def test(self, request: Request, pk: str = None) -> Response:
        """Send a test ping event to this webhook."""
        webhook = self.get_object()
        payload = {
            'event': 'ping',
            'timestamp': timezone.now().isoformat(),
            'webhook_id': webhook.id,
            'message': 'Webhook test from Altassian.',
        }
        delivery = _dispatch_webhook(webhook, 'ping', payload)
        return Response(WebhookDeliverySerializer(delivery).data)

    @action(detail=True, methods=['get'])
    def deliveries(self, request: Request, pk: str = None) -> Response:
        """List recent delivery attempts for this webhook."""
        webhook = self.get_object()
        qs = webhook.deliveries.all()[:50]
        serializer = WebhookDeliverySerializer(qs, many=True)
        return Response(serializer.data)


def _sign_payload(payload_bytes: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 signature for webhook payload."""
    return hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()


def _dispatch_webhook(webhook: Webhook, event: str, payload: dict) -> WebhookDelivery:
    """Send a webhook event and record the delivery attempt."""
    payload_bytes = json.dumps(payload, default=str).encode()

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Altassian-Webhooks/1.0',
        'X-Webhook-Event': event,
    }

    if webhook.secret:
        headers['X-Webhook-Signature'] = f'sha256={_sign_payload(payload_bytes, webhook.secret)}'

    delivery = WebhookDelivery.objects.create(
        webhook=webhook,
        event=event,
        payload=payload,
        status='pending',
    )

    start = time.monotonic()
    try:
        req = URLRequest(
            webhook.url,
            data=payload_bytes,
            headers=headers,
            method='POST',
        )
        with urlopen(req, timeout=10) as resp:
            status_code = resp.status
            body = resp.read().decode(errors='replace')[:2048]
        duration = int((time.monotonic() - start) * 1000)
        delivery.status = 'success' if 200 <= status_code < 300 else 'failed'
        delivery.status_code = status_code
        delivery.response_body = body
        delivery.duration_ms = duration
    except (URLError, OSError, TimeoutError) as exc:
        duration = int((time.monotonic() - start) * 1000)
        delivery.status = 'failed'
        delivery.error_message = str(exc)[:1024]
        delivery.duration_ms = duration
        logger.warning('Webhook delivery failed for %s: %s', webhook.name, exc)

    delivery.save()
    return delivery


def dispatch_event(event: str, payload: dict) -> list[WebhookDelivery]:
    """Fire an event to all active webhooks subscribed to it."""
    webhooks = Webhook.objects.filter(is_active=True, events__contains=[event])
    deliveries = []
    for webhook in webhooks:
        delivery = _dispatch_webhook(webhook, event, payload)
        deliveries.append(delivery)
    return deliveries
