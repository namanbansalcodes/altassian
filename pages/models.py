from django.db import models

class Page(models.Model):
    title = models.CharField(max_length=200)
    space = models.ForeignKey('spaces.Space', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    body_markdown = models.TextField()
    body_html = models.TextField()
    created_by = models.ForeignKey('user_accounts.CustomUser', related_name='pages_created', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('user_accounts.CustomUser', related_name='pages_updated', on_delete=models.CASCADE)
    position = models.IntegerField()
    is_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PageVersion(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    version_number = models.IntegerField()
    body_markdown = models.TextField()
    edited_by = models.ForeignKey('user_accounts.CustomUser', related_name='page_versions_edited', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Version {self.version_number} of {self.page.title}"

class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    author = models.ForeignKey('user_accounts.CustomUser', on_delete=models.CASCADE)
    body = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[:20]

class Attachment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_by = models.ForeignKey('user_accounts.CustomUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
