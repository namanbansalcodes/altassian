"""User and Organization models."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Organization(models.Model):
    """Singleton: there is exactly one Organization row in this single-org MVP."""
    name = models.CharField(max_length=200)
    logo_url = models.URLField(blank=True, default="")
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_singleton(cls) -> "Organization":
        org = cls.objects.first()
        if org is None:
            raise Organization.DoesNotExist("No Organization row exists. Run create_admin.")
        return org


class CustomUserManager(BaseUserManager):
    """Email is the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", CustomUser.Role.ADMIN)
        return self._create_user(email, password, **extra)


class CustomUser(AbstractUser):
    """Email-as-username user with org role."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    username = None  # disabled
    email = models.EmailField("email address", unique=True)
    display_name = models.CharField(max_length=120, blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN
