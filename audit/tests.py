from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from user_accounts.models import CustomUser
from .models import AuditLog
from .utils import log_action


class AuditLogModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='auditor', password='Password123!', email='audit@test.com',
        )

    def test_log_action_creates_entry(self):
        entry = log_action(
            user=self.user,
            action='CREATE',
            resource_type='Page',
            resource_id='42',
            detail='Created test page',
        )
        self.assertEqual(entry.user, self.user)
        self.assertEqual(entry.action, 'CREATE')
        self.assertEqual(entry.resource_type, 'Page')
        self.assertEqual(entry.resource_id, '42')
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_log_action_anonymous(self):
        entry = log_action(
            user=None,
            action='LOGIN',
            resource_type='Session',
        )
        self.assertIsNone(entry.user)
        self.assertEqual(entry.action, 'LOGIN')

    def test_str_representation(self):
        entry = log_action(
            user=self.user,
            action='UPDATE',
            resource_type='Space',
            resource_id='DEV',
        )
        self.assertIn('auditor', str(entry))
        self.assertIn('UPDATE', str(entry))


class AuditLogAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            username='admin', password='Password123!', email='admin@test.com', role='admin',
        )
        self.viewer = CustomUser.objects.create_user(
            username='viewer', password='Password123!', email='viewer@test.com', role='viewer',
        )
        for i in range(3):
            log_action(user=self.admin, action='CREATE', resource_type='Page', resource_id=str(i))

    def test_admin_can_list_audit_logs(self):
        self.client.force_authenticate(self.admin)
        r = self.client.get('/api/audit/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 3)

    def test_viewer_cannot_list_audit_logs(self):
        self.client.force_authenticate(self.viewer)
        r = self.client.get('/api/audit/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_audit_logs(self):
        r = self.client.get('/api/audit/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_action(self):
        log_action(user=self.admin, action='DELETE', resource_type='Page', resource_id='99')
        self.client.force_authenticate(self.admin)
        r = self.client.get('/api/audit/', {'action': 'DELETE'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)

    def test_filter_by_resource_type(self):
        log_action(user=self.admin, action='CREATE', resource_type='Space', resource_id='HR')
        self.client.force_authenticate(self.admin)
        r = self.client.get('/api/audit/', {'resource_type': 'Space'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)
