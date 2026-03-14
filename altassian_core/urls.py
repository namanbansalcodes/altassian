from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.routers import DefaultRouter

from altassian_core.views import HealthCheckView
from spaces.views import SpaceViewSet
from pages.views import PageViewSet, PageVersionViewSet, CommentViewSet, AttachmentViewSet
from user_accounts.views import CustomUserViewSet

router = DefaultRouter()
router.register(r'spaces', SpaceViewSet)
router.register(r'pages', PageViewSet)
router.register(r'page-versions', PageVersionViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'attachments', AttachmentViewSet)
router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', HealthCheckView.as_view(), name='health_check'),
    path('api/', include(router.urls)),
    path('api/', include('user_accounts.urls')),
    path('api/search/', include('search.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/audit/', include('audit.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/', include('projects.urls')),
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
