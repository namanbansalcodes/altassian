from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import ACCESS_COOKIE, REFRESH_COOKIE
from .invite_models import Invite
from .invite_serializers import (
    InviteAcceptSerializer,
    InviteCreateSerializer,
    InvitePublicSerializer,
)
from .permissions import IsAdmin
from .serializers import UserSerializer
from .views import _set_cookie

User = get_user_model()


def _send_invite_email(invite: Invite) -> None:
    accept_url = f"{settings.PUBLIC_BASE_URL}/invite/{invite.token}"
    body = (
        f"You've been invited to Altassian.\n\n"
        f"Accept your invite: {accept_url}\n\n"
        f"Token: {invite.token}\n"
        f"Expires: {invite.expires_at:%Y-%m-%d %H:%M UTC}\n"
    )
    send_mail(
        subject="You're invited to Altassian",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite.email],
        fail_silently=False,
    )


class InviteListCreateView(generics.ListCreateAPIView):
    serializer_class = InviteCreateSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    queryset = Invite.objects.all()

    def perform_create(self, serializer):
        invite = serializer.save(invited_by=self.request.user)
        _send_invite_email(invite)


class InviteDeleteView(generics.DestroyAPIView):
    serializer_class = InviteCreateSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    queryset = Invite.objects.all()


class InviteByTokenView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def get(self, request, token):
        invite = get_object_or_404(Invite, token=token)
        if not invite.is_valid():
            return Response({"detail": "Invite expired or already accepted."}, status=status.HTTP_410_GONE)
        return Response(InvitePublicSerializer(invite).data)


class InviteAcceptView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request, token):
        invite = get_object_or_404(Invite, token=token)
        if not invite.is_valid():
            return Response({"detail": "Invite expired or already accepted."}, status=status.HTTP_410_GONE)
        s = InviteAcceptSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        with transaction.atomic():
            user = User.objects.create_user(
                email=invite.email,
                password=s.validated_data["password"],
                display_name=s.validated_data["display_name"],
                role=User.Role.MEMBER,
                is_active=True,
            )
            invite.accepted_at = timezone.now()
            invite.save(update_fields=["accepted_at"])

        refresh = RefreshToken.for_user(user)
        resp = Response(UserSerializer(user).data)
        _set_cookie(resp, ACCESS_COOKIE, str(refresh.access_token), settings.JWT_ACCESS_LIFETIME)
        _set_cookie(resp, REFRESH_COOKIE, str(refresh), settings.JWT_REFRESH_LIFETIME)
        return resp
