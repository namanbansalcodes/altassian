from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

from .models import Notification


def notify(
    *,
    recipient: AbstractUser,
    actor: AbstractUser | None = None,
    verb: str,
    target_type: str,
    target_id: int,
    message: str,
) -> Notification:
    """Create an in-app notification. Skips if recipient == actor."""
    if actor and recipient.pk == actor.pk:
        return None  # type: ignore[return-value]
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        target_type=target_type,
        target_id=target_id,
        message=message,
    )
