import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


def _default_expiry():
    return timezone.now() + timedelta(days=settings.INVITE_TTL_DAYS)


class Invite(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, default=_generate_token)
    invited_by = models.ForeignKey("user_accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="invites_sent")
    expires_at = models.DateTimeField(default=_default_expiry)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def is_valid(self) -> bool:
        return self.accepted_at is None and self.expires_at > timezone.now()

    def __str__(self) -> str:
        return f"Invite<{self.email}>"
