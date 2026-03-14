from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from user_accounts.models import CustomUser
from .models import Notification
from .utils import notify


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='recipient', password='Password123!', email='r@test.com',
        )
        self.actor = CustomUser.objects.create_user(
            username='actor', password='Password123!', email='a@test.com',
        )

    def test_notify_creates_notification(self):
        n = notify(
            recipient=self.user,
            actor=self.actor,
            verb='page_updated',
            target_type='Page',
            target_id=1,
            message='actor updated "My Page"',
        )
        self.assertIsNotNone(n)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertFalse(n.is_read)

    def test_notify_skips_self_notification(self):
        n = notify(
            recipient=self.user,
            actor=self.user,
            verb='page_updated',
            target_type='Page',
            target_id=1,
            message='You updated "My Page"',
        )
        self.assertIsNone(n)
        self.assertEqual(Notification.objects.count(), 0)

    def test_str_representation(self):
        n = notify(
            recipient=self.user,
            actor=self.actor,
            verb='comment_added',
            target_type='Comment',
            target_id=5,
            message='actor commented on "My Page"',
        )
        self.assertIn('comment_added', str(n))
        self.assertIn('recipient', str(n))


class NotificationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='user1', password='Password123!', email='u1@test.com',
        )
        self.other = CustomUser.objects.create_user(
            username='user2', password='Password123!', email='u2@test.com',
        )
        # Create notifications for user1
        for i in range(5):
            Notification.objects.create(
                recipient=self.user,
                actor=self.other,
                verb='page_updated',
                target_type='Page',
                target_id=i,
                message=f'user2 updated page {i}',
            )
        # One for another user (should not be visible)
        Notification.objects.create(
            recipient=self.other,
            actor=self.user,
            verb='page_created',
            target_type='Page',
            target_id=99,
            message='user1 created page 99',
        )

    def test_list_own_notifications(self):
        self.client.force_authenticate(self.user)
        r = self.client.get('/api/notifications/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 5)

    def test_cannot_see_others_notifications(self):
        self.client.force_authenticate(self.user)
        r = self.client.get('/api/notifications/')
        ids = [n['id'] for n in r.data['results']]
        other_notif = Notification.objects.filter(recipient=self.other).first()
        self.assertNotIn(other_notif.id, ids)

    def test_unread_count(self):
        self.client.force_authenticate(self.user)
        r = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['unread_count'], 5)

    def test_mark_single_read(self):
        self.client.force_authenticate(self.user)
        notif = Notification.objects.filter(recipient=self.user).first()
        r = self.client.patch(f'/api/notifications/{notif.id}/read/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data['is_read'])

    def test_mark_all_read(self):
        self.client.force_authenticate(self.user)
        r = self.client.post('/api/notifications/mark-all-read/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['marked_read'], 5)
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, is_read=False).count(), 0,
        )

    def test_delete_notification(self):
        self.client.force_authenticate(self.user)
        notif = Notification.objects.filter(recipient=self.user).first()
        r = self.client.delete(f'/api/notifications/{notif.id}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.filter(recipient=self.user).count(), 4)

    def test_unauthenticated_access_denied(self):
        r = self.client.get('/api/notifications/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_read_status(self):
        self.client.force_authenticate(self.user)
        # Mark one as read
        notif = Notification.objects.filter(recipient=self.user).first()
        notif.is_read = True
        notif.save()
        r = self.client.get('/api/notifications/', {'is_read': 'true'})
        self.assertEqual(r.data['count'], 1)
        r = self.client.get('/api/notifications/', {'is_read': 'false'})
        self.assertEqual(r.data['count'], 4)
