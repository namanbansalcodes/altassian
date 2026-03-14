from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, EmailVerificationToken, LoginAttempt


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'email_verified', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_staff', 'is_active', 'email_verified']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar', 'bio', 'role', 'email_verified')}),
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['username', 'success', 'locked_out', 'ip_address', 'timestamp']
    list_filter = ['success', 'locked_out']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['username', 'ip_address', 'user_agent', 'success', 'locked_out', 'timestamp']
    ordering = ['-timestamp']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    readonly_fields = ['user', 'token', 'created_at']
