import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = [('admin', 'Admin'), ('editor', 'Editor'), ('viewer', 'Viewer')]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Verification'),
    ]

    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions_set')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='viewer', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=128, blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be 9-15 digits, optionally prefixed with +.',
        )],
        help_text='E.164 format recommended, e.g. +14155552671',
    )
    phone_verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['email'], name='idx_user_email'),
            models.Index(fields=['date_joined'], name='idx_user_date_joined'),
            models.Index(fields=['status'], name='idx_user_status'),
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


class PhoneVerificationToken(models.Model):
    """Stores phone verification codes (OTP) with expiry."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='phone_verification_token',
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(
        default=0,
        help_text='Number of failed verification attempts for this code.',
    )

    def __str__(self) -> str:
        return f'Phone verification for {self.user.username}'

    def is_expired(self) -> bool:
        expiry_minutes = getattr(settings, 'PHONE_VERIFICATION_EXPIRY_MINUTES', 10)
        return timezone.now() > self.created_at + timezone.timedelta(minutes=expiry_minutes)

    def max_attempts_exceeded(self) -> bool:
        max_attempts = getattr(settings, 'PHONE_VERIFICATION_MAX_ATTEMPTS', 5)
        return self.attempts >= max_attempts

    @staticmethod
    def generate_code() -> str:
        """Generate a cryptographically secure 6-digit OTP."""
        return f'{secrets.randbelow(1000000):06d}'
