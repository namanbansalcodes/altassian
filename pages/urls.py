from rest_framework.routers import DefaultRouter

from .views import PageViewSet

router = DefaultRouter(trailing_slash=True)
router.register("pages", PageViewSet, basename="page")

urlpatterns = router.urls
