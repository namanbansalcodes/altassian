"""user_accounts views — cookie-based auth (Phase D1)."""
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import ACCESS_COOKIE, REFRESH_COOKIE
from .serializers import LoginSerializer, UserSerializer


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


class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = authenticate(request, email=s.validated_data["email"], password=s.validated_data["password"])
        if user is None or not user.is_active:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        resp = Response(UserSerializer(user).data)
        _set_cookie(resp, ACCESS_COOKIE, str(refresh.access_token), settings.JWT_ACCESS_LIFETIME)
        _set_cookie(resp, REFRESH_COOKIE, str(refresh), settings.JWT_REFRESH_LIFETIME)
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
        from django.contrib.auth import get_user_model

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

        user = get_user_model().objects.get(pk=user_id)
        new_refresh = RefreshToken.for_user(user)
        resp = Response({"detail": "ok"})
        _set_cookie(resp, ACCESS_COOKIE, str(new_refresh.access_token), settings.JWT_ACCESS_LIFETIME)
        _set_cookie(resp, REFRESH_COOKIE, str(new_refresh), settings.JWT_REFRESH_LIFETIME)
        return resp


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)
