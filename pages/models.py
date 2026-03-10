from django.db import models
from django.conf import settings

class Page(models.Model):
    title = models.CharField(max_length=255)
    space = models.ForeignKey('spaces.Space', on_delete=models.CASCADE, related_name='pages')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    body_markdown = models.TextField()
    body_html = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_pages')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='updated_pages')
    position = models.PositiveIntegerField()
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class PageVersion(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    body_markdown = models.TextField()
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='page_versions')
    created_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(blank=True)

    def __str__(self):
        return f"{self.page.title} v{self.version_number}"

class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.page}"

class Attachment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attachments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
