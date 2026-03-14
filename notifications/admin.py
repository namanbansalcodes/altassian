from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'recipient', 'verb', 'target_type', 'target_id', 'is_read')
    list_filter = ('verb', 'is_read', 'target_type')
    search_fields = ('recipient__username', 'message')
    readonly_fields = ('recipient', 'actor', 'verb', 'target_type', 'target_id', 'message', 'created_at')
