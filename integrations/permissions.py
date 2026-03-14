from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request


class APIKeyScopePermission(BasePermission):
    """
    Enforce API key scope when request is authenticated via API key.

    - 'read' scope: only safe methods (GET, HEAD, OPTIONS)
    - 'write' scope: all non-admin operations
    - 'admin' scope: unrestricted

    Requests not using API key auth are always allowed through this permission.
    """

    def has_permission(self, request: Request, view: object) -> bool:
        api_key = getattr(request, 'api_key', None)
        if api_key is None:
            return True

        scope = api_key.scope
        if scope == 'admin':
            return True
        if scope == 'write':
            return True
        if scope == 'read':
            return request.method in SAFE_METHODS

        return False
