from rest_framework.routers import DefaultRouter

from .views import SpaceViewSet

router = DefaultRouter(trailing_slash=True)
router.register("", SpaceViewSet, basename="space")

urlpatterns = router.urls
