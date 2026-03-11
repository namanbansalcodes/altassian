from django.contrib import admin
from .models import Page, PageVersion, Comment, Attachment


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'space', 'created_by', 'is_draft', 'created_at', 'updated_at']
    list_filter = ['is_draft', 'space', 'created_at']
    search_fields = ['title', 'body_markdown']


@admin.register(PageVersion)
class PageVersionAdmin(admin.ModelAdmin):
    list_display = ['page', 'version_number', 'edited_by', 'created_at']
    list_filter = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['page', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['body']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['file', 'page', 'uploaded_by', 'created_at']
    list_filter = ['created_at']
