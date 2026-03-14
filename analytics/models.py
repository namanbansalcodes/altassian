from django.conf import settings
from django.db import models


class PageView(models.Model):
    """Tracks individual page view events for analytics."""
    page = models.ForeignKey(
        'pages.Page',
        on_delete=models.CASCADE,
        related_name='views',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='page_views',
    )
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    session_id = models.CharField(max_length=64, blank=True, default='')

    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['page', 'viewed_at']),
            models.Index(fields=['user', 'viewed_at']),
        ]

    def __str__(self) -> str:
        return f"View of {self.page} by {self.user or 'anonymous'} at {self.viewed_at}"
