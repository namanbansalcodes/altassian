from django.contrib import admin
from integrations.models import APIKey, Webhook, WebhookDelivery


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'prefix', 'user', 'scope', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['is_active', 'scope']
    search_fields = ['name', 'prefix', 'user__username']
    readonly_fields = ['prefix', 'hashed_key', 'created_at', 'last_used_at']


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'user', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'url', 'user__username']


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['webhook', 'event', 'status', 'status_code', 'attempted_at', 'duration_ms']
    list_filter = ['status', 'event']
    readonly_fields = ['webhook', 'event', 'payload', 'status', 'status_code', 'response_body', 'error_message', 'attempted_at', 'duration_ms']
