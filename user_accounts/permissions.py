from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request


class IsOwnerOrReadOnly(BasePermission):
    """Allow owners to edit their own user object; everyone else gets read-only."""

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user


class IsAdmin(BasePermission):
    """Only allow users with the 'admin' role."""

    def has_permission(self, request: Request, view: object) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'admin'
        )


class IsEditorOrAbove(BasePermission):
    """Allow users with 'admin' or 'editor' role."""

    def has_permission(self, request: Request, view: object) -> bool:
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) in ('admin', 'editor')
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin can do anything; others get read-only access."""

    def has_permission(self, request: Request, view: object) -> bool:
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'admin'
        )


class IsEditorOrAboveOrReadOnly(BasePermission):
    """Editors and admins can write; viewers get read-only access."""

    def has_permission(self, request: Request, view: object) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, 'role', None) in ('admin', 'editor')


class IsContentOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allow the content creator or an admin to modify.
    Expects the object to have a field matching one of the common owner patterns.
    """

    OWNER_FIELDS = ('created_by', 'author', 'uploaded_by', 'owner')

    def has_object_permission(self, request: Request, view: object, obj: object) -> bool:
        if request.method in SAFE_METHODS:
            return True
        if getattr(request.user, 'role', None) == 'admin':
            return True
        for field in self.OWNER_FIELDS:
            owner = getattr(obj, field, None)
            if owner is not None:
                return owner == request.user
        return False
