import hashlib
import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone

OTP_TTL_MINUTES = 10
OTP_LENGTH = 6


def _generate_code() -> str:
    return f"{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}"


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _default_expiry():
    return timezone.now() + timedelta(minutes=OTP_TTL_MINUTES)


class OneTimeCode(models.Model):
    email = models.EmailField(db_index=True)
    code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField(default=_default_expiry)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    @classmethod
    def issue(cls, email: str) -> tuple["OneTimeCode", str]:
        code = _generate_code()
        otp = cls.objects.create(email=email.lower().strip(), code_hash=_hash_code(code))
        return otp, code

    @classmethod
    def consume(cls, email: str, code: str) -> "OneTimeCode | None":
        normalized = email.lower().strip()
        candidate = (
            cls.objects.filter(email=normalized, used_at__isnull=True, expires_at__gt=timezone.now())
            .order_by("-created_at")
            .first()
        )
        if candidate is None:
            return None
        if candidate.code_hash != _hash_code(code):
            return None
        candidate.used_at = timezone.now()
        candidate.save(update_fields=["used_at"])
        return candidate

    def __str__(self) -> str:
        return f"OTP<{self.email} @ {self.created_at:%Y-%m-%d %H:%M}>"
