import logging
import secrets

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
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

from altassian_core.throttles import LoginRateThrottle
from .auth_serializers import (
    FastTokenObtainPairSerializer,
    PhoneVerificationConfirmSerializer,
    PhoneVerificationSendSerializer,
)
from .models import CustomUser, EmailVerificationToken, LoginAttempt, PhoneVerificationToken
from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer

logger = logging.getLogger('altassian')


class FastTokenObtainPairView(TokenObtainPairView):
    serializer_class = FastTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


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


class EmailVerificationSendView(APIView):
    """Send (or re-send) an email verification link to the authenticated user."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = request.user
        if user.email_verified:
            return Response(
                {'detail': 'Email is already verified.'},
                status=status.HTTP_200_OK,
            )

        # Generate a secure token
        token = secrets.token_urlsafe(48)

        # Upsert verification token
        EmailVerificationToken.objects.update_or_create(
            user=user,
            defaults={'token': token},
        )

        # Build verification URL
        frontend_url = getattr(settings, 'FRONTEND_EMAIL_VERIFY_URL', '')
        if frontend_url:
            verify_link = f'{frontend_url}?token={token}'
        else:
            verify_link = f'token={token}'

        send_mail(
            subject='Altassian – Verify Your Email Address',
            message=(
                f'Hello {user.username},\n\n'
                f'Please verify your email address by clicking the link below:\n\n'
                f'{verify_link}\n\n'
                f'If you did not create this account, you can safely ignore this email.'
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@altassian.local'),
            recipient_list=[user.email],
            fail_silently=True,
        )

        return Response(
            {'detail': 'Verification email sent.'},
            status=status.HTTP_200_OK,
        )


class EmailVerificationConfirmView(APIView):
    """Confirm an email verification token."""
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        token = request.data.get('token', '').strip()
        if not token:
            return Response(
                {'detail': 'Verification token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            verification = EmailVerificationToken.objects.select_related('user').get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired verification token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if verification.is_expired():
            verification.delete()
            return Response(
                {'detail': 'Verification token has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = verification.user
        user.email_verified = True
        # Auto-activate if both email and phone are verified (or no phone on file)
        if user.status == 'pending' and (user.phone_verified or not user.phone_number):
            user.status = 'active'
            user.save(update_fields=['email_verified', 'status'])
        else:
            user.save(update_fields=['email_verified'])
        verification.delete()

        return Response(
            {'detail': 'Email verified successfully.'},
            status=status.HTTP_200_OK,
        )


class LoginHistoryView(APIView):
    """Return recent login attempts for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        attempts = LoginAttempt.objects.filter(
            username__iexact=request.user.username,
        ).order_by('-timestamp')[:20]

        data = [
            {
                'ip_address': a.ip_address,
                'user_agent': a.user_agent,
                'success': a.success,
                'locked_out': a.locked_out,
                'timestamp': a.timestamp.isoformat(),
            }
            for a in attempts
        ]
        return Response({'results': data}, status=status.HTTP_200_OK)


class PhoneVerificationSendView(APIView):
    """Send a verification code to the user's phone number via SMS."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = request.user
        serializer = PhoneVerificationSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Optionally update phone number from request
        new_phone = serializer.validated_data.get('phone_number')
        if new_phone:
            if new_phone != user.phone_number:
                user.phone_number = new_phone
                user.phone_verified = False
                user.save(update_fields=['phone_number', 'phone_verified'])

        if not user.phone_number:
            return Response(
                {'detail': 'No phone number on file. Please add a phone number first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.phone_verified:
            return Response(
                {'detail': 'Phone number is already verified.'},
                status=status.HTTP_200_OK,
            )

        # Generate OTP code
        code = PhoneVerificationToken.generate_code()

        # Upsert verification token
        PhoneVerificationToken.objects.update_or_create(
            user=user,
            defaults={'code': code, 'attempts': 0},
        )

        # Send SMS (pluggable backend — logs in dev, real SMS in prod)
        sms_backend = getattr(settings, 'SMS_BACKEND', 'console')
        if sms_backend == 'console':
            logger.info(
                'Phone verification code for %s (%s): %s',
                user.username, user.phone_number, code,
            )
        else:
            # Production: integrate with SMS provider (Twilio, etc.)
            _send_sms(user.phone_number, code)

        return Response(
            {'detail': 'Verification code sent to your phone number.'},
            status=status.HTTP_200_OK,
        )


class PhoneVerificationConfirmView(APIView):
    """Confirm a phone verification code."""
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = PhoneVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        code = serializer.validated_data['code']

        try:
            token = PhoneVerificationToken.objects.get(user=user)
        except PhoneVerificationToken.DoesNotExist:
            return Response(
                {'detail': 'No pending verification. Please request a new code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token.is_expired():
            token.delete()
            return Response(
                {'detail': 'Verification code has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token.max_attempts_exceeded():
            token.delete()
            return Response(
                {'detail': 'Too many failed attempts. Please request a new code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not secrets.compare_digest(token.code, code):
            token.attempts += 1
            token.save(update_fields=['attempts'])
            remaining = getattr(settings, 'PHONE_VERIFICATION_MAX_ATTEMPTS', 5) - token.attempts
            return Response(
                {'detail': f'Invalid code. {max(remaining, 0)} attempts remaining.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Success — mark phone as verified
        user.phone_verified = True
        # If both email and phone are verified, activate the user
        if user.email_verified and user.status == 'pending':
            user.status = 'active'
            user.save(update_fields=['phone_verified', 'status'])
        else:
            user.save(update_fields=['phone_verified'])
        token.delete()

        return Response(
            {'detail': 'Phone number verified successfully.'},
            status=status.HTTP_200_OK,
        )


def _send_sms(phone_number: str, code: str) -> None:
    """Send an SMS with the verification code. Override for production SMS provider."""
    sms_provider = getattr(settings, 'SMS_PROVIDER', None)
    if sms_provider == 'twilio':
        from twilio.rest import Client  # type: ignore[import-untyped]
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
        )
        client.messages.create(
            body=f'Your Altassian verification code is: {code}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )
    else:
        logger.warning('No SMS provider configured. Code for %s: %s', phone_number, code)
