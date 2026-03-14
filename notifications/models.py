from django.conf import settings
from django.db import models


class Notification(models.Model):
    """In-app notification delivered to a user when content they care about changes."""

    VERB_CHOICES = [
        ('page_created', 'Page created'),
        ('page_updated', 'Page updated'),
        ('page_deleted', 'Page deleted'),
        ('comment_added', 'Comment added'),
        ('comment_reply', 'Comment reply'),
        ('mentioned', 'Mentioned'),
        ('role_changed', 'Role changed'),
        ('space_archived', 'Space archived'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_sent',
    )
    verb = models.CharField(max_length=30, choices=VERB_CHOICES)
    target_type = models.CharField(max_length=50, help_text="e.g. Page, Comment, Space")
    target_id = models.PositiveIntegerField()
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at'], name='idx_notif_recipient_unread'),
        ]

    def __str__(self) -> str:
        return f"[{self.verb}] → {self.recipient.username}: {self.message[:60]}"
