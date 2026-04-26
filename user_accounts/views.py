"""user_accounts views — cookie-based auth (OTP-only)."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from altassian_core.throttles import LoginRateThrottle

from .authentication import ACCESS_COOKIE, REFRESH_COOKIE
from .otp_models import OneTimeCode
from .serializers import OtpRequestSerializer, OtpVerifySerializer, UserSerializer

User = get_user_model()


def _set_cookie(response, name: str, value: str, lifetime: int) -> None:
    response.set_cookie(
        name,
        value,
        max_age=lifetime,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/" if name == ACCESS_COOKIE else "/api/auth/",
    )


def _delete_cookie(response, name: str) -> None:
    response.delete_cookie(name, path="/" if name == ACCESS_COOKIE else "/api/auth/")


def _issue_jwt(response, user) -> None:
    refresh = RefreshToken.for_user(user)
    _set_cookie(response, ACCESS_COOKIE, str(refresh.access_token), settings.JWT_ACCESS_LIFETIME)
    _set_cookie(response, REFRESH_COOKIE, str(refresh), settings.JWT_REFRESH_LIFETIME)


def _send_otp_email(email: str, code: str) -> None:
    send_mail(
        subject="Your Altassian sign-in code",
        message=(
            f"Your Altassian sign-in code is:\n\n"
            f"    {code}\n\n"
            f"It expires in 10 minutes. If you didn't request it, ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


class OtpRequestView(APIView):
    """Request a 6-digit code by email. Always returns 200 to avoid email enumeration."""

    permission_classes = (AllowAny,)
    authentication_classes: list = []
    throttle_classes = (LoginRateThrottle,)

    def post(self, request):
        s = OtpRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data["email"].lower().strip()
        _, code = OneTimeCode.issue(email)
        _send_otp_email(email, code)
        return Response({"detail": "If the email is valid, a code has been sent."})


class OtpVerifyView(APIView):
    """Verify code; create user if first time, log in by setting JWT cookies."""

    permission_classes = (AllowAny,)
    authentication_classes: list = []
    throttle_classes = (LoginRateThrottle,)

    def post(self, request):
        s = OtpVerifySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data["email"].lower().strip()
        code = s.validated_data["code"]
        display_name = s.validated_data.get("display_name", "")

        otp = OneTimeCode.consume(email=email, code=code)
        if otp is None:
            return Response(
                {"detail": "Invalid or expired code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "display_name": display_name or email.split("@")[0],
                "role": User.Role.MEMBER,
                "is_active": True,
            },
        )
        if not created and not user.is_active:
            return Response({"detail": "Account is inactive."}, status=status.HTTP_403_FORBIDDEN)
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        resp = Response(UserSerializer(user).data)
        _issue_jwt(resp, user)
        return resp


class LogoutView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if raw_refresh:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass
        resp = Response(status=status.HTTP_204_NO_CONTENT)
        _delete_cookie(resp, ACCESS_COOKIE)
        _delete_cookie(resp, REFRESH_COOKIE)
        return resp


class RefreshView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if not raw_refresh:
            return Response({"detail": "No refresh cookie."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            old = RefreshToken(raw_refresh)
        except (InvalidToken, TokenError):
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = old["user_id"]
        try:
            old.blacklist()
        except TokenError:
            pass

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"detail": "User is inactive."}, status=status.HTTP_401_UNAUTHORIZED)
        resp = Response({"detail": "ok"})
        _issue_jwt(resp, user)
        return resp


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)
