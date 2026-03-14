from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .auth_serializers import FastTokenObtainPairSerializer
from .models import CustomUser
from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer


class FastTokenObtainPairView(TokenObtainPairView):
    serializer_class = FastTokenObtainPairSerializer


class LogoutView(APIView):
    """Blacklist the provided refresh token to invalidate the session."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Token is invalid or already blacklisted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Forgotten-password step 1: user submits their email.

    If the email belongs to an active account, a reset link is sent.
    The response is always 200 to prevent email enumeration.
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        # Always return success to prevent email enumeration attacks
        try:
            user = CustomUser.objects.get(email__iexact=email, is_active=True)
        except CustomUser.DoesNotExist:
            return Response(
                {'detail': 'If an account with that email exists, a password reset link has been sent.'},
                status=status.HTTP_200_OK,
            )

        # Generate token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Build reset URL (frontend consumes uid + token)
        frontend_url = getattr(settings, 'FRONTEND_PASSWORD_RESET_URL', '')
        if frontend_url:
            reset_link = f'{frontend_url}?uid={uid}&token={token}'
        else:
            reset_link = f'uid={uid}&token={token}'

        # Send email
        send_mail(
            subject='Altassian – Password Reset Request',
            message=(
                f'Hello {user.username},\n\n'
                f'You requested a password reset. Use the following link to set a new password:\n\n'
                f'{reset_link}\n\n'
                f'If you did not request this, you can safely ignore this email.\n\n'
                f'This link will expire in {settings.PASSWORD_RESET_TIMEOUT // 3600} hour(s).'
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@altassian.local'),
            recipient_list=[user.email],
            fail_silently=True,
        )

        return Response(
            {'detail': 'If an account with that email exists, a password reset link has been sent.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Forgotten-password step 2: user submits uid, token, and new password.

    Validates the token, enforces password strength, and updates the password.
    """
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_str = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        # Extract UID from request (sent separately for flexibility)
        uid_b64 = request.data.get('uid', '')
        if not uid_b64:
            return Response(
                {'detail': 'User identifier is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Decode UID
        try:
            uid = force_str(urlsafe_base64_decode(uid_b64))
            user = CustomUser.objects.get(pk=uid, is_active=True)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response(
                {'detail': 'Invalid or expired reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify token
        if not default_token_generator.check_token(user, token_str):
            return Response(
                {'detail': 'Invalid or expired reset link. Please request a new password reset.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        user.set_password(new_password)
        user.save(update_fields=['password'])

        return Response(
            {'detail': 'Password has been reset successfully. You can now log in with your new password.'},
            status=status.HTTP_200_OK,
        )
