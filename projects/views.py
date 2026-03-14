from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from user_accounts.permissions import IsEditorOrAboveOrReadOnly, IsContentOwnerOrAdmin
from projects.models import Project, Task
from projects.serializers import (
    ProjectSerializer,
    ProjectDetailSerializer,
    TaskSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD for projects. Editors+ can create; owners/admins can modify."""

    queryset = Project.objects.select_related("owner").all()
    permission_classes = [IsAuthenticated, IsEditorOrAboveOrReadOnly, IsContentOwnerOrAdmin]
    filterset_fields = ["status", "owner"]
    search_fields = ["name", "key", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    lookup_field = "key"

    def get_serializer_class(self) -> type:
        if self.action == "retrieve":
            return ProjectDetailSerializer
        return ProjectSerializer

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request: Request, key: str = None) -> Response:
        """Add a user to the project by user ID."""
        from django.contrib.auth import get_user_model

        project = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        project.members.add(user)
        return Response({"detail": f"{user.username} added to project."})

    @action(detail=True, methods=["post"], url_path="remove-member")
    def remove_member(self, request: Request, key: str = None) -> Response:
        """Remove a user from the project by user ID."""
        from django.contrib.auth import get_user_model

        project = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if user == project.owner:
            return Response(
                {"detail": "Cannot remove the project owner."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project.members.remove(user)
        return Response({"detail": f"{user.username} removed from project."})


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks. Editors+ can create; reporters/assignees/admins can modify."""

    queryset = Task.objects.select_related(
        "project", "assignee", "reporter"
    ).all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsEditorOrAboveOrReadOnly]
    filterset_fields = ["project", "status", "priority", "assignee", "reporter"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "priority", "status", "due_date", "created_at", "updated_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        project_key = self.request.query_params.get("project_key")
        if project_key:
            qs = qs.filter(project__key=project_key)
        return qs

    @action(detail=True, methods=["patch"])
    def assign(self, request: Request, pk: str = None) -> Response:
        """Assign or reassign a task to a user by user ID."""
        task = self.get_object()
        assignee_id = request.data.get("assignee_id")
        if assignee_id is None:
            task.assignee = None
            task.save(update_fields=["assignee", "updated_at"])
            return Response({"detail": "Task unassigned."})
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(pk=assignee_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        task.assignee = user
        task.save(update_fields=["assignee", "updated_at"])
        serializer = self.get_serializer(task)
        return Response(serializer.data)
