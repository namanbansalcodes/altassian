from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from user_accounts.otp_models import OneTimeCode


class Command(BaseCommand):
    help = "Delete consumed and expired OTPs older than --days (default 7)."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7)

    def handle(self, *args, **opts):
        cutoff = timezone.now() - timedelta(days=opts["days"])
        deleted, _ = OneTimeCode.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} OTP rows older than {opts['days']}d"))
