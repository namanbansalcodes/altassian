from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Tracks significant user actions across the platform for compliance and debugging."""

    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('ROLE_CHANGE', 'Role Change'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, help_text="e.g. Page, Space, User")
    resource_id = models.CharField(max_length=100, blank=True, default='')
    detail = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp'], name='idx_audit_user_ts'),
            models.Index(fields=['action', 'timestamp'], name='idx_audit_action_ts'),
            models.Index(fields=['resource_type', 'resource_id'], name='idx_audit_resource'),
        ]

    def __str__(self) -> str:
        user_str = self.user.username if self.user else 'anonymous'
        return f"[{self.timestamp}] {user_str} {self.action} {self.resource_type} {self.resource_id}"
