from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .auth_views import (
    EmailVerificationConfirmView,
    EmailVerificationSendView,
    FastTokenObtainPairView,
    LoginHistoryView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PhoneVerificationConfirmView,
    PhoneVerificationSendView,
)

urlpatterns = [
    path('auth/login/', FastTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/email-verify/', EmailVerificationSendView.as_view(), name='email_verify_send'),
    path('auth/email-verify/confirm/', EmailVerificationConfirmView.as_view(), name='email_verify_confirm'),
    path('auth/phone-verify/', PhoneVerificationSendView.as_view(), name='phone_verify_send'),
    path('auth/phone-verify/confirm/', PhoneVerificationConfirmView.as_view(), name='phone_verify_confirm'),
    path('auth/login-history/', LoginHistoryView.as_view(), name='login_history'),
]
