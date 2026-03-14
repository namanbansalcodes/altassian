from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import time

from .models import CustomUser


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login_and_me(self):
        r = self.client.post('/api/users/register/', {
            'username': 'charlie', 'email': 'c@example.com', 'password': 'Password123!', 'password_confirm': 'Password123!',
            'first_name': 'Charlie', 'last_name': 'Day'
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        t0 = time.monotonic()
        t = self.client.post('/api/auth/login/', {'username': 'charlie', 'password': 'Password123!'})
        t1 = time.monotonic()
        self.assertEqual(t.status_code, status.HTTP_200_OK)
        # Login should be reasonably fast under typical dev envs
        self.assertLess(t1 - t0, 1.5, f"login too slow: {(t1 - t0)*1000:.1f}ms")
        # Response should include the user payload to avoid immediate /me call
        self.assertIn('user', t.data)
        access = t.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        m0 = time.monotonic()
        me = self.client.get('/api/users/me/')
        m1 = time.monotonic()
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data['username'], 'charlie')
        self.assertLess(m1 - m0, 1.0, f"/users/me too slow: {(m1 - m0)*1000:.1f}ms")

    def test_jwt_token_refresh(self):
        CustomUser.objects.create_user(username='dave', password='Password123!', email='d@example.com')
        login = self.client.post('/api/auth/login/', {'username': 'dave', 'password': 'Password123!'})
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn('access', login.data)
        self.assertIn('refresh', login.data)
        # Refresh the token
        t0 = time.monotonic()
        refresh = self.client.post('/api/auth/token/refresh/', {'refresh': login.data['refresh']})
        t1 = time.monotonic()
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh.data)
        self.assertLess(t1 - t0, 1.0, f"token refresh too slow: {(t1 - t0)*1000:.1f}ms")

    def test_login_invalid_credentials(self):
        CustomUser.objects.create_user(username='eve', password='Password123!', email='e@example.com')
        resp = self.client.post('/api/auth/login/', {'username': 'eve', 'password': 'WrongPass!'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_unauthenticated(self):
        resp = self.client.get('/api/users/me/')
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class APISmokeTests(TestCase):
    """Basic smoke tests to verify all API endpoints are reachable."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='smoke', password='Password123!', email='smoke@example.com')
        resp = self.client.post('/api/auth/login/', {'username': 'smoke', 'password': 'Password123!'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_list_endpoints_return_200(self):
        for url in ['/api/users/', '/api/spaces/', '/api/pages/', '/api/page-versions/', '/api/comments/', '/api/attachments/']:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, status.HTTP_200_OK, f'{url} returned {resp.status_code}')

    def test_register_duplicate_username_rejected(self):
        self.client.credentials()  # clear auth
        payload = {
            'username': 'smoke', 'email': 'smoke2@example.com',
            'password': 'Password123!', 'password_confirm': 'Password123!',
        }
        resp = self.client.post('/api/users/register/', payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
