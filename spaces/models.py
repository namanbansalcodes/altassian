from django.db import models


class Space(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=64, blank=True, default="")  # emoji or short URL
    position = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        "user_accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="spaces_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "name")

    def __str__(self) -> str:
        return self.name
