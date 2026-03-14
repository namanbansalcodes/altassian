from django.urls import path, include
from rest_framework.routers import DefaultRouter

from integrations.views import APIKeyViewSet, WebhookViewSet

router = DefaultRouter()
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'webhooks', WebhookViewSet, basename='webhook')

urlpatterns = [
    path('', include(router.urls)),
]
