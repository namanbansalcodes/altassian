from django.db import models

class Space(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='owned_spaces')
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name
