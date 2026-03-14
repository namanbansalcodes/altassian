from django.contrib import admin

from analytics.models import PageView


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['page', 'user', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['page__title', 'user__username']
    raw_id_fields = ['page', 'user']
