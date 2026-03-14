from rest_framework import serializers

from projects.models import Project, Task


class ProjectSerializer(serializers.ModelSerializer):
    owner_username: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="owner.username"
    )
    task_count: serializers.SerializerMethodField = serializers.SerializerMethodField()
    member_count: serializers.SerializerMethodField = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "key",
            "description",
            "owner",
            "owner_username",
            "status",
            "task_count",
            "member_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_task_count(self, obj: Project) -> int:
        return obj.tasks.count()

    def get_member_count(self, obj: Project) -> int:
        return obj.members.count()

    def create(self, validated_data: dict) -> Project:
        validated_data["owner"] = self.context["request"].user
        project = super().create(validated_data)
        project.members.add(project.owner)
        return project


class ProjectDetailSerializer(ProjectSerializer):
    members = serializers.SlugRelatedField(
        many=True, slug_field="username", read_only=True
    )

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ["members"]


class TaskSerializer(serializers.ModelSerializer):
    assignee_username: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="assignee.username", default=None
    )
    reporter_username: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="reporter.username"
    )
    project_key: serializers.ReadOnlyField = serializers.ReadOnlyField(
        source="project.key"
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "project_key",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_username",
            "reporter",
            "reporter_username",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reporter", "created_at", "updated_at"]

    def create(self, validated_data: dict) -> Task:
        validated_data["reporter"] = self.context["request"].user
        return super().create(validated_data)
