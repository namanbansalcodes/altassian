from django.core.management.base import BaseCommand
from django.db import transaction

from pages.models import Page
from spaces.models import Space
from user_accounts.models import CustomUser, Organization


class Command(BaseCommand):
    help = "Seed a demo org with admin + member, two spaces, a few pages. Idempotent."

    def handle(self, *args, **opts):
        with transaction.atomic():
            org, _ = Organization.objects.get_or_create(pk=1, defaults={"name": "Altassian Demo"})
            admin, _ = CustomUser.objects.get_or_create(
                email="admin@altassian.local",
                defaults={
                    "display_name": "Admin",
                    "role": CustomUser.Role.ADMIN,
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                },
            )
            admin.set_password("adminpass123"); admin.save()

            member, _ = CustomUser.objects.get_or_create(
                email="alice@altassian.local",
                defaults={"display_name": "Alice", "role": CustomUser.Role.MEMBER, "is_active": True},
            )
            member.set_password("alicepass123"); member.save()

            eng, _ = Space.objects.get_or_create(slug="eng", defaults={"name": "Engineering", "created_by": admin})
            prod, _ = Space.objects.get_or_create(slug="prod", defaults={"name": "Product", "created_by": admin})

            for space, title, body in [
                (eng, "Architecture", "# Architecture\n\nDjango + Next.js."),
                (eng, "Onboarding", "# Onboarding\n\nWelcome aboard."),
                (prod, "Roadmap", "# Roadmap\n\n- [ ] ship MVP\n- [ ] dogfood\n"),
            ]:
                Page.objects.get_or_create(
                    space=space, slug=title.lower(),
                    defaults={"title": title, "body_md": body, "created_by": admin, "updated_by": admin},
                )

            self.stdout.write(self.style.SUCCESS("Seeded. Login admin@altassian.local / adminpass123."))
