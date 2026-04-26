from django.urls import path

from .views import LogoutView, MeView, OtpRequestView, OtpVerifyView, RefreshView

urlpatterns = [
    path("otp/request", OtpRequestView.as_view()),
    path("otp/verify", OtpVerifyView.as_view()),
    path("logout", LogoutView.as_view()),
    path("refresh", RefreshView.as_view()),
    path("me", MeView.as_view()),
]
