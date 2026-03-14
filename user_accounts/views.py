from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .permissions import IsAdmin, IsOwnerOrReadOnly
from .serializers import (
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    CustomUserSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.only(
        'id', 'username', 'email', 'first_name', 'last_name',
        'avatar', 'bio', 'role', 'date_joined',
    )
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
