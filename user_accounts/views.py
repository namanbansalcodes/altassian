from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, LoginAttempt
from .permissions import IsAdmin, IsOwnerOrReadOnly
from .serializers import (
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    CustomUserSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    @action(detail=False, methods=['get', 'patch', 'put', 'delete'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request: Request) -> Response:
        user = request.user

        if request.method == 'GET':
            serializer = CustomUserSerializer(user)
            return Response(serializer.data)

        if request.method in ('PATCH', 'PUT'):
            partial = request.method == 'PATCH'
            serializer = ProfileUpdateSerializer(
                user, data=request.data, partial=partial, context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(CustomUserSerializer(user).data)

        if request.method == 'DELETE':
            user.is_active = False
            user.save(update_fields=['is_active'])
            return Response({'detail': 'Account deactivated successfully.'}, status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        return CustomUser.objects.only(
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'bio', 'role', 'status', 'date_joined',
            'email_verified', 'phone_number', 'phone_verified',
        )

    @action(detail=False, methods=['get'], url_path='me/activity', permission_classes=[IsAuthenticated])
    def activity_summary(self, request: Request) -> Response:
        """Return an activity summary for the authenticated user."""
        user = request.user

        # Count pages created
        pages_created = 0
        comments_made = 0
        spaces_owned = 0

        try:
            from pages.models import Page, Comment
            pages_created = Page.objects.filter(created_by=user).count()
            comments_made = Comment.objects.filter(author=user).count()
        except Exception:
            pass

        try:
            from spaces.models import Space
            spaces_owned = Space.objects.filter(owner=user).count()
        except Exception:
            pass

        # Recent login activity
        recent_logins = LoginAttempt.objects.filter(
            username__iexact=user.username, success=True,
        ).order_by('-timestamp')[:5]

        last_login_attempts = [
            {
                'ip_address': a.ip_address,
                'timestamp': a.timestamp.isoformat(),
            }
            for a in recent_logins
        ]

        return Response({
            'username': user.username,
            'role': user.role,
            'status': user.status,
            'email_verified': user.email_verified,
            'phone_verified': user.phone_verified,
            'pages_created': pages_created,
            'comments_made': comments_made,
            'spaces_owned': spaces_owned,
            'recent_logins': last_login_attempts,
        })

    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            **CustomUserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='change-password', permission_classes=[IsAuthenticated])
    def change_password(self, request: Request) -> Response:
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='role', permission_classes=[IsAdmin])
    def update_role(self, request: Request, pk: str = None) -> Response:
        """Admin-only endpoint to change a user's role."""
        user = self.get_object()
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CustomUserSerializer(user).data)

    @action(detail=True, methods=['patch'], url_path='status', permission_classes=[IsAdmin])
    def update_status(self, request: Request, pk: str = None) -> Response:
        """Admin-only endpoint to change a user's status (active/suspended/pending)."""
        user = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {'detail': 'status field is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_statuses = [c[0] for c in CustomUser.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'detail': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.status = new_status
        # Sync is_active with status
        user.is_active = new_status != 'suspended'
        user.save(update_fields=['status', 'is_active'])
        return Response(CustomUserSerializer(user).data)

    @action(detail=True, methods=['patch'], url_path='activate', permission_classes=[IsAdmin])
    def activate(self, request: Request, pk: str = None) -> Response:
        """Admin-only endpoint to activate/deactivate a user account."""
        user = self.get_object()
        if 'is_active' not in request.data:
            return Response({'detail': 'is_active field is required.'}, status=status.HTTP_400_BAD_REQUEST)
        is_active = request.data.get('is_active')
        if isinstance(is_active, str):
            user.is_active = is_active.lower() in ('true', '1')
        else:
            user.is_active = bool(is_active)
        user.save(update_fields=['is_active'])
        return Response(CustomUserSerializer(user).data)
