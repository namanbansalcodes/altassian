from django.urls import path, include
from rest_framework.routers import DefaultRouter

from integrations.views import APIKeyViewSet, WebhookViewSet
from integrations.export_views import ExportSpaceView, ImportSpaceView, BulkPagesView

router = DefaultRouter()
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'webhooks', WebhookViewSet, basename='webhook')

urlpatterns = [
    path('', include(router.urls)),
    path('export/<str:space_key>/', ExportSpaceView.as_view(), name='export-space'),
    path('import/', ImportSpaceView.as_view(), name='import-space'),
    path('bulk/pages/', BulkPagesView.as_view(), name='bulk-pages'),
]
