from django.contrib import admin

from .models import Attachment, Comment, Page, PageVersion


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "space", "slug", "is_public", "is_draft", "deleted_at", "updated_at")
    search_fields = ("title", "slug")
    list_filter = ("space", "is_public", "is_draft")


@admin.register(PageVersion)
class PageVersionAdmin(admin.ModelAdmin):
    list_display = ("page", "version_n", "edited_by", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("page", "author", "created_at", "deleted_at")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("page", "original_filename", "mime_type", "size_bytes", "uploaded_by", "created_at")
