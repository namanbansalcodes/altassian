from django.db import models

class Space(models.Model):
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey('user_accounts.CustomUser', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, default='')
    meta_keywords = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.name
