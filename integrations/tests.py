from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from integrations.models import APIKey, Webhook, WebhookDelivery, generate_api_key, hash_api_key
from user_accounts.models import CustomUser


class APIKeyModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='testpass123', role='editor',
        )

    def test_generate_api_key_format(self):
        key = generate_api_key()
        self.assertTrue(key.startswith('alt_'))
        self.assertGreater(len(key), 20)

    def test_hash_api_key_deterministic(self):
        key = 'alt_test_key_123'
        h1 = hash_api_key(key)
        h2 = hash_api_key(key)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_api_key_validity(self):
        from django.utils import timezone
        from datetime import timedelta

        raw_key = generate_api_key()
        api_key = APIKey.objects.create(
            name='test', prefix=raw_key[:12],
            hashed_key=hash_api_key(raw_key),
            user=self.user, scope='read',
        )
        self.assertTrue(api_key.is_valid)

        api_key.is_active = False
        api_key.save()
        self.assertFalse(api_key.is_valid)

        api_key.is_active = True
        api_key.expires_at = timezone.now() - timedelta(hours=1)
        api_key.save()
        self.assertTrue(api_key.is_expired)
        self.assertFalse(api_key.is_valid)


class APIKeyAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='apiuser', password='testpass123', role='editor',
        )
        self.raw_key = generate_api_key()
        self.api_key = APIKey.objects.create(
            name='test-key', prefix=self.raw_key[:12],
            hashed_key=hash_api_key(self.raw_key),
            user=self.user, scope='read',
        )

    def test_auth_via_api_key_header(self):
        response = self.client.get(
            '/api/spaces/',
            HTTP_X_API_KEY=self.raw_key,
        )
        self.assertIn(response.status_code, [200, 301])

    def test_invalid_api_key_rejected(self):
        response = self.client.get(
            '/api/spaces/',
            HTTP_X_API_KEY='alt_invalid_key_12345',
        )
        self.assertIn(response.status_code, [401, 403])

    def test_deactivated_key_rejected(self):
        self.api_key.is_active = False
        self.api_key.save()
        response = self.client.get(
            '/api/spaces/',
            HTTP_X_API_KEY=self.raw_key,
        )
        self.assertIn(response.status_code, [401, 403])

    def test_read_scope_permission_class(self):
        """Verify APIKeyScopePermission denies write for read-only keys."""
        from integrations.permissions import APIKeyScopePermission
        from unittest.mock import MagicMock
        perm = APIKeyScopePermission()
        mock_request = MagicMock()
        mock_request.method = 'POST'
        mock_request.api_key = self.api_key
        self.assertFalse(perm.has_permission(mock_request, None))
        mock_request.method = 'GET'
        self.assertTrue(perm.has_permission(mock_request, None))


class APIKeyViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='keyowner', password='testpass123', role='editor',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_api_key(self):
        response = self.client.post(
            '/api/integrations/api-keys/',
            {'name': 'my-key', 'scope': 'read'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('raw_key', response.data)
        self.assertTrue(response.data['raw_key'].startswith('alt_'))

    def test_list_api_keys(self):
        raw = generate_api_key()
        APIKey.objects.create(
            name='listed', prefix=raw[:12],
            hashed_key=hash_api_key(raw),
            user=self.user, scope='read',
        )
        response = self.client.get('/api/integrations/api-keys/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_revoke_api_key(self):
        raw = generate_api_key()
        key = APIKey.objects.create(
            name='revokable', prefix=raw[:12],
            hashed_key=hash_api_key(raw),
            user=self.user, scope='read',
        )
        response = self.client.patch(f'/api/integrations/api-keys/{key.id}/revoke/')
        self.assertEqual(response.status_code, 200)
        key.refresh_from_db()
        self.assertFalse(key.is_active)

    def test_non_admin_cannot_create_admin_scope(self):
        response = self.client.post(
            '/api/integrations/api-keys/',
            {'name': 'admin-key', 'scope': 'admin'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)


class WebhookViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='hookuser', password='testpass123', role='editor',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_webhook(self):
        response = self.client.post(
            '/api/integrations/webhooks/',
            {
                'name': 'my-hook',
                'url': 'https://example.com/webhook',
                'events': ['page.created', 'page.updated'],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Webhook.objects.count(), 1)

    def test_webhook_requires_https(self):
        response = self.client.post(
            '/api/integrations/webhooks/',
            {
                'name': 'bad-hook',
                'url': 'http://example.com/webhook',
                'events': ['page.created'],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_webhook_validates_events(self):
        response = self.client.post(
            '/api/integrations/webhooks/',
            {
                'name': 'bad-events',
                'url': 'https://example.com/webhook',
                'events': ['invalid.event'],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_list_webhooks(self):
        Webhook.objects.create(
            name='hook1', url='https://example.com/h1',
            events=['page.created'], user=self.user,
        )
        response = self.client.get('/api/integrations/webhooks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)


class ExportImportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='exportuser', password='testpass123', role='editor',
        )
        self.client.force_authenticate(user=self.user)

        from spaces.models import Space
        from pages.models import Page
        self.space = Space.objects.create(
            name='Export Test', key='EXP', owner=self.user,
        )
        self.page = Page.objects.create(
            title='Test Page', space=self.space,
            body_markdown='# Hello', body_html='<h1>Hello</h1>',
            created_by=self.user, updated_by=self.user, position=0,
        )

    def test_export_space(self):
        response = self.client.get('/api/integrations/export/EXP/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['space']['key'], 'EXP')
        self.assertEqual(len(data['pages']), 1)

    def test_export_nonexistent_space(self):
        response = self.client.get('/api/integrations/export/NOPE/')
        self.assertEqual(response.status_code, 404)

    def test_import_space(self):
        import_data = {
            'format_version': '1.0',
            'space': {'name': 'Imported', 'key': 'IMP', 'description': 'test'},
            'pages': [
                {
                    'title': 'Imported Page',
                    'slug': 'imported-page',
                    'body_markdown': '# Imported',
                    'body_html': '<h1>Imported</h1>',
                    'position': 0,
                    'is_draft': False,
                    'versions': [],
                },
            ],
        }
        response = self.client.post(
            '/api/integrations/import/',
            import_data,
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['pages_imported'], 1)

    def test_import_duplicate_space_rejected(self):
        import_data = {
            'space': {'name': 'Export Test', 'key': 'EXP'},
            'pages': [],
        }
        response = self.client.post(
            '/api/integrations/import/',
            import_data,
            format='json',
        )
        self.assertEqual(response.status_code, 409)


class BulkPagesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='bulkuser', password='testpass123', role='editor',
        )
        self.client.force_authenticate(user=self.user)

        from spaces.models import Space
        self.space = Space.objects.create(
            name='Bulk Test', key='BLK', owner=self.user,
        )

    def test_bulk_create_pages(self):
        response = self.client.post(
            '/api/integrations/bulk/pages/',
            {
                'space_key': 'BLK',
                'pages': [
                    {'title': 'Page 1', 'body_markdown': 'content 1', 'body_html': '', 'position': 0},
                    {'title': 'Page 2', 'body_markdown': 'content 2', 'body_html': '', 'position': 1},
                ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['created_count'], 2)

    def test_bulk_update_status(self):
        from pages.models import Page
        p1 = Page.objects.create(
            title='Draft1', space=self.space, body_markdown='',
            body_html='', created_by=self.user, updated_by=self.user,
            position=0, is_draft=True,
        )
        response = self.client.patch(
            '/api/integrations/bulk/pages/',
            {'page_ids': [p1.id], 'action': 'publish'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        p1.refresh_from_db()
        self.assertFalse(p1.is_draft)


class SecurityHeadersTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_security_headers_present(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertIn('strict-origin', response['Referrer-Policy'])
