from django.conf import settings
from django.db import models


class Project(models.Model):
    """A project that groups related tasks together."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("archived", "Archived"),
        ("completed", "Completed"),
    ]

    name: models.CharField = models.CharField(max_length=255)
    key: models.SlugField = models.SlugField(max_length=10, unique=True)
    description: models.TextField = models.TextField(blank=True, default="")
    owner: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    members: models.ManyToManyField = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        blank=True,
    )
    status: models.CharField = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.key} - {self.name}"


class Task(models.Model):
    """A task within a project, assignable to a user."""

    STATUS_CHOICES = [
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("in_review", "In Review"),
        ("done", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    project: models.ForeignKey = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    title: models.CharField = models.CharField(max_length=255)
    description: models.TextField = models.TextField(blank=True, default="")
    status: models.CharField = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="todo", db_index=True
    )
    priority: models.CharField = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium", db_index=True
    )
    assignee: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    reporter: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reported_tasks",
    )
    due_date: models.DateField = models.DateField(null=True, blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assignee", "status"]),
        ]

    def __str__(self) -> str:
        return self.title
