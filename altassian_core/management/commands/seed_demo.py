from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from spaces.models import Space
from pages.models import Page, Comment


class Command(BaseCommand):
    help = 'Seed demo data: users, spaces, pages, comments'

    def handle(self, *args, **options):
        User = get_user_model()
        # Users
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'User'
        })
        if not admin.password:
            admin.set_password('Password123!')
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
        alice, _ = User.objects.get_or_create(username='alice', defaults={
            'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'A'
        })
        if not alice.password:
            alice.set_password('Password123!'); alice.save()
        bob, _ = User.objects.get_or_create(username='bob', defaults={
            'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'B'
        })
        if not bob.password:
            bob.set_password('Password123!'); bob.save()

        # Spaces
        eng, _ = Space.objects.get_or_create(key='ENG', defaults={'name': 'Engineering', 'owner': admin, 'description': 'Engineering docs'})
        prd, _ = Space.objects.get_or_create(key='PRD', defaults={'name': 'Product', 'owner': alice, 'description': 'Product planning'})

        # Pages tree under ENG
        home, _ = Page.objects.get_or_create(space=eng, title='Home', defaults={
            'body_markdown': '# Welcome to Engineering', 'body_html': '<h1>Welcome to Engineering</h1>',
            'created_by': admin, 'updated_by': admin, 'position': 1
        })
        runbook, _ = Page.objects.get_or_create(space=eng, title='Runbook', defaults={
            'parent': home, 'body_markdown': 'Runbook details', 'body_html': '<p>Runbook details</p>',
            'created_by': admin, 'updated_by': admin, 'position': 1
        })
        oncall, _ = Page.objects.get_or_create(space=eng, title='On-call', defaults={
            'parent': home, 'body_markdown': 'On-call', 'body_html': '<p>On-call</p>',
            'created_by': admin, 'updated_by': admin, 'position': 2
        })

        # Pages under PRD
        roadmap, _ = Page.objects.get_or_create(space=prd, title='Roadmap', defaults={
            'body_markdown': 'Q1 Goals', 'body_html': '<p>Q1 Goals</p>',
            'created_by': alice, 'updated_by': alice, 'position': 1
        })

        # Comments
        Comment.objects.get_or_create(page=home, author=alice, body='Looks good!')
        Comment.objects.get_or_create(page=home, author=bob, body='Add more details please')

        self.stdout.write(self.style.SUCCESS('Seeded demo data.'))
