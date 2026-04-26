from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AttachmentDeleteView,
    AttachmentUploadView,
    CommentDeleteView,
    CommentListCreateView,
    PageViewSet,
)

router = DefaultRouter(trailing_slash=True)
router.register("pages", PageViewSet, basename="page")

urlpatterns = router.urls + [
    path("pages/<int:page_pk>/comments", CommentListCreateView.as_view({"get": "list", "post": "create"})),
    path("comments/<int:pk>", CommentDeleteView.as_view({"delete": "destroy"})),
    path("pages/<int:page_pk>/attachments", AttachmentUploadView.as_view({"post": "create"})),
    path("attachments/<int:pk>", AttachmentDeleteView.as_view({"delete": "destroy"})),
]
