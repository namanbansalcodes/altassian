"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("user_accounts.urls")),
    path("api/spaces/", include("spaces.urls")),
    path("api/", include("pages.urls")),
    path("api/search/", include("search.urls")),
]
