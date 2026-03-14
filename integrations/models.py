import hashlib
import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_api_key() -> str:
    """Generate a cryptographically secure API key."""
    return f"alt_{secrets.token_urlsafe(48)}"


def hash_api_key(raw_key: str) -> str:
    """Hash an API key using SHA-256 for secure storage."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


class APIKey(models.Model):
    """API key for programmatic/service-to-service authentication."""

    SCOPE_CHOICES = [
        ('read', 'Read Only'),
        ('write', 'Read & Write'),
        ('admin', 'Full Admin Access'),
    ]

    name = models.CharField(max_length=255, help_text='Human-readable label for this key.')
    prefix = models.CharField(
        max_length=12, db_index=True,
        help_text='First 8 chars of the key for identification.',
    )
    hashed_key = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys',
    )
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='read')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_apikey_user_created'),
            models.Index(fields=['is_active', 'expires_at'], name='idx_apikey_active_expiry'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.prefix}...)'

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired

    def record_usage(self) -> None:
        APIKey.objects.filter(pk=self.pk).update(last_used_at=timezone.now())


class Webhook(models.Model):
    """Webhook endpoint for event notifications to external services."""

    EVENT_CHOICES = [
        ('page.created', 'Page Created'),
        ('page.updated', 'Page Updated'),
        ('page.deleted', 'Page Deleted'),
        ('comment.created', 'Comment Created'),
        ('comment.deleted', 'Comment Deleted'),
        ('space.created', 'Space Created'),
        ('space.updated', 'Space Updated'),
        ('space.deleted', 'Space Deleted'),
        ('user.registered', 'User Registered'),
    ]

    name = models.CharField(max_length=255)
    url = models.URLField(max_length=2048, help_text='HTTPS endpoint to receive events.')
    secret = models.CharField(
        max_length=128, blank=True, default='',
        help_text='Shared secret for HMAC-SHA256 payload signing.',
    )
    events = models.JSONField(
        default=list,
        help_text='List of event types this webhook subscribes to.',
    )
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='webhooks',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active'], name='idx_webhook_active'),
            models.Index(fields=['user', '-created_at'], name='idx_webhook_user_created'),
        ]

    def __str__(self) -> str:
        return f'{self.name} -> {self.url}'


class WebhookDelivery(models.Model):
    """Log of webhook delivery attempts."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event = models.CharField(max_length=50)
    payload = models.JSONField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    attempted_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['webhook', '-attempted_at'], name='idx_delivery_webhook_ts'),
            models.Index(fields=['status'], name='idx_delivery_status'),
        ]

    def __str__(self) -> str:
        return f'{self.event} -> {self.webhook.name} ({self.status})'
