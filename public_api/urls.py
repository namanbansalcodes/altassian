from django.urls import path

from .views import PublicPageView

urlpatterns = [
    path("spaces/<slug:space_slug>/pages/<slug:page_slug>", PublicPageView.as_view()),
]
