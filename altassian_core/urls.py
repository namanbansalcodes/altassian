"""Root URL configuration."""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from .views import HealthCheckView

# Admin path is env-driven so prod can move it off /admin/. Strip a trailing
# slash if the user supplied one; Django adds the trailing slash itself.
_admin_prefix = settings.ADMIN_URL_PREFIX.strip("/")

urlpatterns = [
    path(f"{_admin_prefix}/", admin.site.urls),
    path("api/health", HealthCheckView.as_view()),
    path("api/auth/", include("user_accounts.urls")),
    path("api/", include("user_accounts.invite_urls")),
    path("api/spaces/", include("spaces.urls")),
    path("api/", include("pages.urls")),
    path("api/search/", include("search.urls")),
    path("api/public/", include("public_api.urls")),
]
