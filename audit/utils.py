from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from rest_framework.request import Request

from .models import AuditLog


def get_client_ip(request: Request) -> str | None:
    """Extract client IP from request, respecting X-Forwarded-For."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(
    *,
    user: AbstractUser | None,
    action: str,
    resource_type: str,
    resource_id: str = '',
    detail: str = '',
    request: Request | None = None,
) -> AuditLog:
    """Create an audit log entry."""
    ip_address = None
    user_agent = ''
    if request is not None:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:512]

    return AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        detail=detail,
        ip_address=ip_address,
        user_agent=user_agent,
    )
