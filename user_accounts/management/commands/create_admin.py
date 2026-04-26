import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from user_accounts.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = "Create the singleton Organization (if missing) and a first admin user."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--org-name", default="Altassian")
        parser.add_argument("--display-name", default="")

    def handle(self, *args, **opts):
        email = opts["email"].lower().strip()
        with transaction.atomic():
            org, created_org = Organization.objects.get_or_create(
                pk=1, defaults={"name": opts["org_name"]}
            )
            if not created_org and org.name != opts["org_name"]:
                self.stdout.write(self.style.WARNING(f"Org already named {org.name!r}; not renaming"))

            if User.objects.filter(email=email).exists():
                self.stderr.write(self.style.ERROR(f"User {email!r} already exists"))
                sys.exit(1)

            user = User.objects.create_superuser(
                email=email,
                password=opts["password"],
                display_name=opts["display_name"] or email.split("@")[0],
                role=User.Role.ADMIN,
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin {user.email} in org {org.name!r}"))
