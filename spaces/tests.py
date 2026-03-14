from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from user_accounts.models import CustomUser
from .models import Space


class SpacesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='bob', password='Password123!', email='b@example.com', role='editor')
        resp = self.client.post('/api/auth/login/', {'username': 'bob', 'password': 'Password123!'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_create_space_sets_owner_and_lookup_by_key(self):
        resp = self.client.post('/api/spaces/', {'name': 'Design', 'key': 'DSN', 'description': 'Design space'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        space = Space.objects.get(key='DSN')
        self.assertEqual(space.owner, self.user)
        # detail by key
        d = self.client.get('/api/spaces/DSN/')
        self.assertEqual(d.status_code, status.HTTP_200_OK)
        self.assertEqual(d.data['key'], 'DSN')
