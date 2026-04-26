from django.contrib import admin

from .models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "position", "created_by", "created_at")
    search_fields = ("slug", "name")
