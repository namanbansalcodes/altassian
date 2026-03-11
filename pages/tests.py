from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from user_accounts.models import CustomUser
from spaces.models import Space
from .models import Page, PageVersion, Comment, Attachment


class PagesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='alice', password='Password123!', email='a@example.com')
        # JWT login
        resp = self.client.post('/api/auth/login/', {'username': 'alice', 'password': 'Password123!'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        self.space = Space.objects.create(name='Engineering', key='ENG', owner=self.user)

    def test_create_page_and_versioning_and_tree(self):
        # Create root page
        resp = self.client.post('/api/pages/', {
            'title': 'Home',
            'space': self.space.id,
            'body_markdown': '# Welcome',
            'body_html': '<h1>Welcome</h1>',
            'position': 1,
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        page_id = resp.data['id']
        slug = resp.data['slug']
        # Create child page
        resp2 = self.client.post('/api/pages/', {
            'title': 'Child',
            'space': self.space.id,
            'parent': page_id,
            'body_markdown': 'Child',
            'body_html': '<p>Child</p>',
            'position': 1,
        }, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        # Update root page to trigger versioning
        resp3 = self.client.patch(f'/api/pages/{page_id}/', {'body_markdown': '# Updated', 'body_html': '<h1>Updated</h1>'}, format='json')
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        versions = PageVersion.objects.filter(page_id=page_id)
        self.assertEqual(versions.count(), 1)
        # Tree by space key
        tree = self.client.get('/api/pages/tree/', {'space_key': 'ENG'})
        self.assertEqual(tree.status_code, status.HTTP_200_OK)
        self.assertEqual(len(tree.data), 1)
        self.assertEqual(tree.data[0]['title'], 'Home')
        self.assertEqual(tree.data[0]['slug'], slug)
        self.assertEqual(len(tree.data[0]['children']), 1)

    def test_search_and_activity(self):
        Page.objects.create(title='Spec', space=self.space, body_markdown='searchable text', body_html='x', created_by=self.user, updated_by=self.user, position=1)
        res = self.client.get('/api/pages/search/', {'q': 'searchable'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(res.data['count'], 1)
        act = self.client.get('/api/pages/activity/')
        self.assertEqual(act.status_code, status.HTTP_200_OK)

    def test_comments_and_attachments(self):
        page = Page.objects.create(title='Doc', space=self.space, body_markdown='x', body_html='x', created_by=self.user, updated_by=self.user, position=1)
        # Comment
        c1 = self.client.post('/api/comments/', {'page': page.id, 'body': 'First!'}, format='json')
        self.assertEqual(c1.status_code, status.HTTP_201_CREATED)
        c2 = self.client.post('/api/comments/', {'page': page.id, 'body': 'Reply', 'parent': c1.data['id']}, format='json')
        self.assertEqual(c2.status_code, status.HTTP_201_CREATED)
        # Attachment
        f = SimpleUploadedFile('hello.txt', b'hello world', content_type='text/plain')
        up = self.client.post('/api/attachments/', {'page': page.id, 'file': f}, format='multipart')
        self.assertEqual(up.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Attachment.objects.filter(page=page).exists())

    def test_get_by_slug(self):
        p = Page.objects.create(title='Doc', space=self.space, body_markdown='md', body_html='html', created_by=self.user, updated_by=self.user, position=1)
        res = self.client.get('/api/pages/by-slug/', {'space_key': self.space.key, 'slug': p.slug})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], p.id)
