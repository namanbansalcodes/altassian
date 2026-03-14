from django.db import models
from django.utils.text import slugify

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, null=True, blank=True)
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

    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, default='')
    meta_keywords = models.CharField(max_length=255, blank=True, default='')
    og_image = models.URLField(max_length=500, blank=True, default='')
    canonical_url = models.URLField(max_length=500, blank=True, default='')
    noindex = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['space', 'slug'], name='unique_page_slug_per_space')
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or 'page'
            candidate = base
            i = 2
            while Page.objects.filter(space=self.space, slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

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
