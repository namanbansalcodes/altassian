from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from spaces.views import SpaceViewSet
from pages.views import PageViewSet, PageVersionViewSet, CommentViewSet, AttachmentViewSet

router = DefaultRouter()
router.register(r'spaces', SpaceViewSet)
router.register(r'pages', PageViewSet)
router.register(r'page-versions', PageVersionViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'attachments', AttachmentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]