import time

from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status

from .models import CustomUser


class RegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'New',
            'last_name': 'User',
        }

    def test_register_success(self):
        r = self.client.post('/api/users/register/', self.valid_payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['username'], 'newuser')
        self.assertEqual(r.data['email'], 'new@example.com')
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_register_tokens_work_immediately(self):
        r = self.client.post('/api/users/register/', self.valid_payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        me = self.client.get('/api/users/me/')
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data['username'], 'newuser')

    def test_register_missing_fields(self):
        r = self.client.post('/api/users/register/', {'username': 'incomplete'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        payload = {**self.valid_payload, 'password_confirm': 'DifferentPass1!'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', str(r.data))

    def test_register_weak_password(self):
        payload = {**self.valid_payload, 'password': '123', 'password_confirm': '123'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        CustomUser.objects.create_user(username='newuser', password='Password123!', email='existing@example.com')
        r = self.client.post('/api/users/register/', self.valid_payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        CustomUser.objects.create_user(username='other', password='Password123!', email='new@example.com')
        r = self.client.post('/api/users/register/', self.valid_payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(r.data))

    def test_register_duplicate_email_case_insensitive(self):
        CustomUser.objects.create_user(username='other', password='Password123!', email='NEW@example.com')
        r = self.client.post('/api/users/register/', self.valid_payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_normalized_to_lowercase(self):
        payload = {**self.valid_payload, 'email': 'MixedCase@Example.COM'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['email'], 'mixedcase@example.com')

    def test_register_email_required(self):
        payload = {**self.valid_payload}
        payload.pop('email')
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='loginuser', password='Password123!',
            email='login@example.com', role='editor',
        )

    def test_login_success(self):
        r = self.client.post('/api/auth/login/', {'username': 'loginuser', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)

    def test_login_returns_user_data(self):
        r = self.client.post('/api/auth/login/', {'username': 'loginuser', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        user_data = r.data.get('user')
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data['username'], 'loginuser')
        self.assertEqual(user_data['email'], 'login@example.com')
        self.assertEqual(user_data['role'], 'editor')

    def test_login_invalid_password(self):
        r = self.client.post('/api/auth/login/', {'username': 'loginuser', 'password': 'Wrong!'})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        r = self.client.post('/api/auth/login/', {'username': 'nobody', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        r = self.client.post('/api/auth/login/', {'username': 'loginuser'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_performance(self):
        t0 = time.monotonic()
        r = self.client.post('/api/auth/login/', {'username': 'loginuser', 'password': 'Password123!'})
        elapsed = time.monotonic() - t0
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertLess(elapsed, 1.5, f"login too slow: {elapsed*1000:.1f}ms")


class TokenRefreshTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        CustomUser.objects.create_user(username='refreshuser', password='Password123!', email='r@example.com')
        login = self.client.post('/api/auth/login/', {'username': 'refreshuser', 'password': 'Password123!'})
        self.refresh_token = login.data['refresh']
        self.access_token = login.data['access']

    def test_refresh_returns_new_access_token(self):
        r = self.client.post('/api/auth/token/refresh/', {'refresh': self.refresh_token})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('access', r.data)

    def test_refresh_invalid_token(self):
        r = self.client.post('/api/auth/token/refresh/', {'refresh': 'invalidtoken'})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_performance(self):
        t0 = time.monotonic()
        r = self.client.post('/api/auth/token/refresh/', {'refresh': self.refresh_token})
        elapsed = time.monotonic() - t0
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertLess(elapsed, 1.0, f"token refresh too slow: {elapsed*1000:.1f}ms")


class LogoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        CustomUser.objects.create_user(username='logoutuser', password='Password123!', email='lo@example.com')
        login = self.client.post('/api/auth/login/', {'username': 'logoutuser', 'password': 'Password123!'})
        self.access_token = login.data['access']
        self.refresh_token = login.data['refresh']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_logout_success(self):
        r = self.client.post('/api/auth/logout/', {'refresh': self.refresh_token})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_logout_blacklists_refresh_token(self):
        self.client.post('/api/auth/logout/', {'refresh': self.refresh_token})
        # After logout, the refresh token should no longer work
        self.client.credentials()
        r = self.client.post('/api/auth/token/refresh/', {'refresh': self.refresh_token})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_missing_refresh_token(self):
        r = self.client.post('/api/auth/logout/', {})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_invalid_token(self):
        r = self.client.post('/api/auth/logout/', {'refresh': 'invalidtoken'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        self.client.credentials()  # clear auth
        r = self.client.post('/api/auth/logout/', {'refresh': self.refresh_token})
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class MeEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='meuser', password='Password123!', email='me@example.com',
            first_name='Me', last_name='User', role='admin',
        )
        login = self.client.post('/api/auth/login/', {'username': 'meuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_me_returns_user_profile(self):
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['username'], 'meuser')
        self.assertEqual(r.data['email'], 'me@example.com')
        self.assertEqual(r.data['first_name'], 'Me')
        self.assertEqual(r.data['role'], 'admin')

    def test_me_unauthenticated(self):
        self.client.credentials()
        r = self.client.get('/api/users/me/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_me_query_count(self):
        with self.assertNumQueries(1):
            r = self.client.get('/api/users/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_me_performance(self):
        t0 = time.monotonic()
        r = self.client.get('/api/users/me/')
        elapsed = time.monotonic() - t0
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertLess(elapsed, 1.0, f"/users/me too slow: {elapsed*1000:.1f}ms")


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='pwuser', password='OldPassword123!', email='pw@example.com',
        )
        login = self.client.post('/api/auth/login/', {'username': 'pwuser', 'password': 'OldPassword123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_change_password_success(self):
        r = self.client.post('/api/users/change-password/', {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword456!',
        })
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # Verify new password works
        self.client.credentials()
        login = self.client.post('/api/auth/login/', {'username': 'pwuser', 'password': 'NewPassword456!'})
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        r = self.client.post('/api/users/change-password/', {
            'old_password': 'WrongPassword!',
            'new_password': 'NewPassword456!',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_weak_new_password(self):
        r = self.client.post('/api/users/change-password/', {
            'old_password': 'OldPassword123!',
            'new_password': '123',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_missing_fields(self):
        r = self.client.post('/api/users/change-password/', {'old_password': 'OldPassword123!'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_requires_auth(self):
        self.client.credentials()
        r = self.client.post('/api/users/change-password/', {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword456!',
        })
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class AuthPerformanceTests(TestCase):
    """Tests that validate auth endpoint response time optimizations."""

    def setUp(self):
        self.client = APIClient()

    def test_register_single_roundtrip(self):
        t0 = time.monotonic()
        r = self.client.post('/api/users/register/', {
            'username': 'perfuser', 'email': 'perf@example.com',
            'password': 'Password123!', 'password_confirm': 'Password123!',
        })
        t1 = time.monotonic()
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', r.data)
        self.assertIn('refresh', r.data)
        self.assertLess(t1 - t0, 2.0, f"register+tokens too slow: {(t1 - t0)*1000:.1f}ms")

    def test_login_query_count(self):
        """Login should execute minimal DB queries (user lookup + outstanding token insert)."""
        CustomUser.objects.create_user(username='quser', password='Password123!', email='q@example.com')
        with self.assertNumQueries(2):
            resp = self.client.post('/api/auth/login/', {'username': 'quser', 'password': 'Password123!'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


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
        self.client.credentials()
        payload = {
            'username': 'smoke', 'email': 'smoke2@example.com',
            'password': 'Password123!', 'password_confirm': 'Password123!',
        }
        resp = self.client.post('/api/users/register/', payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auth_endpoints_reachable(self):
        """Verify all auth-related URL patterns resolve correctly."""
        # Login
        r = self.client.post('/api/auth/login/', {'username': 'smoke', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # Refresh
        r2 = self.client.post('/api/auth/token/refresh/', {'refresh': r.data['refresh']})
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        r3 = self.client.post('/api/auth/logout/', {'refresh': r.data['refresh']})
        # Token may already be blacklisted from rotation, but endpoint should be reachable
        self.assertIn(r3.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
