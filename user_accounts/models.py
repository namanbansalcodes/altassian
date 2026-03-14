from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions_set')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('editor', 'Editor'), ('viewer', 'Viewer')], default='viewer', db_index=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['date_joined'], name='idx_user_date_joined'),
        ]

    def __str__(self) -> str:
        return self.username


class LoginAttempt(models.Model):
    """Tracks login attempts for security monitoring and account lockout."""
    username = models.CharField(max_length=150, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default='')
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    locked_out = models.BooleanField(
        default=False,
        help_text='True if this attempt was blocked by account lockout.',
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', 'timestamp'], name='idx_login_attempt_user_ts'),
        ]

    def __str__(self) -> str:
        status = 'success' if self.success else 'failed'
        return f'{self.username} - {status} - {self.timestamp}'

    @classmethod
    def recent_failures(cls, username: str, window_minutes: int | None = None) -> int:
        """Count recent consecutive failed attempts for a username."""
        if window_minutes is None:
            window_minutes = getattr(settings, 'ACCOUNT_LOCKOUT_WINDOW_MINUTES', 15)
        cutoff = timezone.now() - timezone.timedelta(minutes=window_minutes)
        return cls.objects.filter(
            username__iexact=username,
            success=False,
            timestamp__gte=cutoff,
        ).count()

    @classmethod
    def is_locked_out(cls, username: str) -> bool:
        """Check if an account is currently locked out due to failed attempts."""
        max_attempts = getattr(settings, 'ACCOUNT_LOCKOUT_MAX_ATTEMPTS', 5)
        return cls.recent_failures(username) >= max_attempts

    @classmethod
    def record(cls, username: str, success: bool, request: object = None,
               locked_out: bool = False) -> 'LoginAttempt':
        """Record a login attempt."""
        ip_address = None
        user_agent = ''
        if request is not None:
            ip_address = (
                request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                or request.META.get('REMOTE_ADDR')
            )
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:512]
        return cls.objects.create(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            locked_out=locked_out,
        )


class EmailVerificationToken(models.Model):
    """Stores email verification tokens with expiry."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='verification_token',
    )
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Verification for {self.user.username}'

    def is_expired(self) -> bool:
        expiry_hours = getattr(settings, 'EMAIL_VERIFICATION_EXPIRY_HOURS', 24)
        return timezone.now() > self.created_at + timezone.timedelta(hours=expiry_hours)
