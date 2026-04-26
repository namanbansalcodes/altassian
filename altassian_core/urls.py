"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path

from .views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", HealthCheckView.as_view()),
    path("api/auth/", include("user_accounts.urls")),
    path("api/", include("user_accounts.invite_urls")),
    path("api/spaces/", include("spaces.urls")),
    path("api/", include("pages.urls")),
    path("api/search/", include("search.urls")),
    path("api/public/", include("public_api.urls")),
]
