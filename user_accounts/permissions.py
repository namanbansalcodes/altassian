from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request


class IsOwnerOrReadOnly(BasePermission):
    """Allow owners to edit their own user object; everyone else gets read-only."""

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user
