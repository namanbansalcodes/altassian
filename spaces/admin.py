from django.contrib import admin
from .models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'owner', 'created_at', 'is_archived']
    list_filter = ['is_archived', 'created_at']
    search_fields = ['name', 'key', 'description']
