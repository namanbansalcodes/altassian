import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils.text import slugify


def _attachment_path(instance: "Attachment", filename: str) -> str:
    return f"attachments/{uuid.uuid4()}/{filename}"


class Page(models.Model):
    space = models.ForeignKey("spaces.Space", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    slug = models.SlugField(max_length=220)
    title = models.CharField(max_length=200)
    body_md = models.TextField(blank=True, default="")
    body_html_cache = models.TextField(blank=True, default="")
    position = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "user_accounts.CustomUser", on_delete=models.CASCADE, related_name="pages_created"
    )
    updated_by = models.ForeignKey(
        "user_accounts.CustomUser", on_delete=models.CASCADE, related_name="pages_updated"
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("space", "slug"),
                condition=models.Q(deleted_at__isnull=True),
                name="unique_active_page_slug_per_space",
            )
        ]
        indexes = [GinIndex(fields=("search_vector",), name="page_search_vector_gin")]
        ordering = ("position", "id")

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "page"
            candidate = base
            i = 2
            while (
                Page.objects.filter(space=self.space, slug=candidate, deleted_at__isnull=True)
                .exclude(pk=self.pk)
                .exists()
            ):
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class PageVersion(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="versions")
    version_n = models.IntegerField()
    body_md = models.TextField()
    edited_by = models.ForeignKey("user_accounts.CustomUser", on_delete=models.CASCADE)
    change_summary = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("page", "version_n"), name="unique_page_version")]
        ordering = ("-version_n",)

    def __str__(self) -> str:
        return f"v{self.version_n} of {self.page_id}"


class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("user_accounts.CustomUser", on_delete=models.CASCADE)
    body_md = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="replies")
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return self.body_md[:30]


class Attachment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=_attachment_path)
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=128, default="application/octet-stream")
    size_bytes = models.BigIntegerField(default=0)
    uploaded_by = models.ForeignKey("user_accounts.CustomUser", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.original_filename
