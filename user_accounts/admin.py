from django.contrib import admin

from .models import CustomUser, Organization


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "display_name", "role", "is_active", "joined_at")
    search_fields = ("email", "display_name")
    list_filter = ("role", "is_active")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
