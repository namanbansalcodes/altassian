import logging
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from integrations.models import APIKey, hash_api_key

logger = logging.getLogger('altassian')


class APIKeyAuthentication(BaseAuthentication):
    """
    Authenticate requests via API key passed in the X-API-Key header.

    The key is hashed and looked up against stored hashed keys.
    Expired or deactivated keys are rejected.
    """

    HEADER = 'HTTP_X_API_KEY'
    AUTH_SCHEME = 'ApiKey'

    def authenticate(self, request: Request) -> tuple | None:
        raw_key = request.META.get(self.HEADER)
        if not raw_key:
            return None

        hashed = hash_api_key(raw_key)
        try:
            api_key = APIKey.objects.select_related('user').get(hashed_key=hashed)
        except APIKey.DoesNotExist:
            logger.warning('API key authentication failed: invalid key (prefix=%s)', raw_key[:12])
            raise AuthenticationFailed('Invalid API key.')

        if not api_key.is_active:
            raise AuthenticationFailed('API key has been deactivated.')

        if api_key.is_expired:
            raise AuthenticationFailed('API key has expired.')

        if not api_key.user.is_active:
            raise AuthenticationFailed('User account is disabled.')

        api_key.record_usage()

        request.api_key = api_key
        return (api_key.user, None)

    def authenticate_header(self, request: Request) -> str:
        return self.AUTH_SCHEME
