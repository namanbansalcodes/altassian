import markdown
from django.core.management.base import BaseCommand

from pages.models import Comment, Page, PageVersion
from spaces.models import Space
from user_accounts.models import CustomUser


class Command(BaseCommand):
    help = "Seed the database with sample users, spaces, and pages"

    def handle(self, *args: object, **options: object) -> None:
        self.stdout.write("Seeding database...")

        # --- Users ---
        admin_user = self._create_user(
            "admin", "admin@altassian.local", "adminpass123",
            role="admin", is_staff=True, is_superuser=True,
            bio="Platform administrator",
        )
        alice = self._create_user(
            "alice", "alice@altassian.local", "alicepass123",
            role="editor", bio="Frontend engineer",
        )
        bob = self._create_user(
            "bob", "bob@altassian.local", "bobpass123",
            role="editor", bio="Backend engineer",
        )
        carol = self._create_user(
            "carol", "carol@altassian.local", "carolpass123",
            role="viewer", bio="Product manager",
        )

        # --- Spaces ---
        eng_space = self._create_space(
            "Engineering", "ENG",
            "Engineering team documentation", admin_user,
        )
        product_space = self._create_space(
            "Product", "PROD",
            "Product specs and roadmaps", carol,
        )
        onboarding_space = self._create_space(
            "Onboarding", "ONB",
            "New hire onboarding guides", admin_user,
        )

        # --- Pages ---
        arch_page = self._create_page(
            eng_space, alice, "Architecture Overview",
            "# Architecture Overview\n\n"
            "Our system uses a **microservices** architecture.\n\n"
            "## Services\n\n"
            "- **API Gateway** — routes requests\n"
            "- **Auth Service** — handles JWT tokens\n"
            "- **Page Service** — manages wiki content\n",
            position=0,
        )
        self._create_page(
            eng_space, bob, "API Reference",
            "# API Reference\n\n"
            "## Authentication\n\n"
            "```\nPOST /api/auth/login/\n"
            "Body: {\"username\": \"...\", \"password\": \"...\"}\n```\n\n"
            "## Spaces\n\n"
            "```\nGET  /api/spaces/\nPOST /api/spaces/\n```\n\n"
            "## Pages\n\n"
            "```\nGET  /api/pages/\nPOST /api/pages/\n```\n",
            position=1, parent=arch_page,
        )
        self._create_page(
            eng_space, bob, "Development Setup",
            "# Development Setup\n\n"
            "1. Clone the repository\n"
            "2. Create a virtual environment: `python -m venv venv`\n"
            "3. Install dependencies: `pip install -r requirements.txt`\n"
            "4. Run migrations: `python manage.py migrate`\n"
            "5. Start the server: `python manage.py runserver`\n",
            position=2,
        )
        roadmap = self._create_page(
            product_space, carol, "Q1 Roadmap",
            "# Q1 Roadmap\n\n"
            "## Goals\n\n"
            "- Launch v1.0 of the wiki platform\n"
            "- Implement real-time collaboration\n"
            "- Add space-level permissions\n\n"
            "## Timeline\n\n"
            "| Milestone | Date |\n"
            "|-----------|------|\n"
            "| Alpha | Jan 15 |\n"
            "| Beta | Feb 28 |\n"
            "| GA | Mar 31 |\n",
            position=0,
        )
        self._create_page(
            onboarding_space, admin_user, "Welcome to Altassian",
            "# Welcome to Altassian!\n\n"
            "Welcome aboard! This guide will help you get started.\n\n"
            "## First Steps\n\n"
            "1. Set up your profile with an avatar and bio\n"
            "2. Browse existing spaces to find your team's docs\n"
            "3. Create your first page\n\n"
            "## Need Help?\n\n"
            "Reach out to the admin team or check the Engineering space.\n",
            position=0,
        )

        # --- Comments ---
        Comment.objects.get_or_create(
            page=roadmap, author=alice,
            defaults={"body": "Looks great! Can we add a stretch goal for search improvements?"},
        )
        Comment.objects.get_or_create(
            page=roadmap, author=bob,
            defaults={"body": "I can take the real-time collaboration piece."},
        )

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    def _create_user(
        self, username: str, email: str, password: str, **extra: object,
    ) -> CustomUser:
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={"email": email, **extra},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f"  Created user: {username}")
        else:
            self.stdout.write(f"  User already exists: {username}")
        return user

    def _create_space(
        self, name: str, key: str, description: str, owner: CustomUser,
    ) -> Space:
        space, created = Space.objects.get_or_create(
            key=key,
            defaults={"name": name, "description": description, "owner": owner},
        )
        if created:
            self.stdout.write(f"  Created space: {name} [{key}]")
        else:
            self.stdout.write(f"  Space already exists: {name} [{key}]")
        return space

    def _create_page(
        self, space: Space, author: CustomUser, title: str,
        body_markdown: str, position: int, parent: Page | None = None,
    ) -> Page:
        body_html = markdown.markdown(body_markdown)
        page, created = Page.objects.get_or_create(
            title=title, space=space,
            defaults={
                "body_markdown": body_markdown,
                "body_html": body_html,
                "created_by": author,
                "updated_by": author,
                "position": position,
                "parent": parent,
            },
        )
        if created:
            PageVersion.objects.create(
                page=page, version_number=1,
                body_markdown=body_markdown,
                edited_by=author,
                change_summary="Initial version",
            )
            self.stdout.write(f"  Created page: {title}")
        else:
            self.stdout.write(f"  Page already exists: {title}")
        return page
