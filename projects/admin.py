from django.contrib import admin

from projects.models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "owner", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "key")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "assignee", "status", "priority", "due_date")
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description")
