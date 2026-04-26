"""DRF auth that reads the access JWT from an httpOnly cookie."""
from rest_framework_simplejwt.authentication import JWTAuthentication


ACCESS_COOKIE = "altassian_access"
REFRESH_COOKIE = "altassian_refresh"


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate by validating the JWT in the `altassian_access` cookie."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if not raw_token:
            return None
        validated = self.get_validated_token(raw_token)
        return self.get_user(validated), validated
