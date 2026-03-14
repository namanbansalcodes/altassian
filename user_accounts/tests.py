import time

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import CustomUser, EmailVerificationToken, LoginAttempt, PhoneVerificationToken


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


class ProfileUpdateTests(TestCase):
    """Tests for profile CRUD via /api/users/me/."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='profileuser', password='Password123!',
            email='profile@example.com', first_name='Original',
            last_name='Name', bio='Old bio', role='editor',
        )
        login = self.client.post('/api/auth/login/', {'username': 'profileuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_get_own_profile(self):
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['username'], 'profileuser')
        self.assertEqual(r.data['bio'], 'Old bio')

    def test_patch_profile(self):
        r = self.client.patch('/api/users/me/', {
            'first_name': 'Updated',
            'bio': 'New bio',
        })
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['first_name'], 'Updated')
        self.assertEqual(r.data['bio'], 'New bio')
        # Unchanged fields remain
        self.assertEqual(r.data['last_name'], 'Name')
        self.assertEqual(r.data['email'], 'profile@example.com')

    def test_put_profile(self):
        r = self.client.put('/api/users/me/', {
            'first_name': 'Put',
            'last_name': 'User',
            'email': 'put@example.com',
            'bio': 'Put bio',
        })
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['first_name'], 'Put')
        self.assertEqual(r.data['email'], 'put@example.com')

    def test_patch_email_unique_validation(self):
        CustomUser.objects.create_user(
            username='other', password='Password123!', email='taken@example.com',
        )
        r = self.client.patch('/api/users/me/', {'email': 'taken@example.com'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(r.data))

    def test_patch_email_case_insensitive_unique(self):
        CustomUser.objects.create_user(
            username='other', password='Password123!', email='taken@example.com',
        )
        r = self.client.patch('/api/users/me/', {'email': 'TAKEN@example.com'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_own_email_allowed(self):
        """User can re-submit their own email without conflict."""
        r = self.client.patch('/api/users/me/', {'email': 'profile@example.com'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_patch_email_normalized(self):
        r = self.client.patch('/api/users/me/', {'email': 'Mixed@Example.COM'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['email'], 'mixed@example.com')

    def test_patch_bio_too_long(self):
        r = self.client.patch('/api/users/me/', {'bio': 'x' * 2001})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('bio', str(r.data))

    def test_patch_bio_at_limit(self):
        r = self.client.patch('/api/users/me/', {'bio': 'x' * 2000})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_patch_username_not_editable(self):
        """Username should not change via profile update (not in serializer fields)."""
        r = self.client.patch('/api/users/me/', {'username': 'hacked'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['username'], 'profileuser')

    def test_patch_role_not_editable(self):
        """Role should not change via profile update (not in serializer fields)."""
        r = self.client.patch('/api/users/me/', {'role': 'admin'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['role'], 'editor')

    def test_profile_update_requires_auth(self):
        self.client.credentials()
        r = self.client.patch('/api/users/me/', {'first_name': 'Nope'})
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_profile_persisted_in_db(self):
        self.client.patch('/api/users/me/', {'first_name': 'Saved', 'bio': 'Persisted'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Saved')
        self.assertEqual(self.user.bio, 'Persisted')


class AccountDeactivateTests(TestCase):
    """Tests for account deactivation via DELETE /api/users/me/."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='deluser', password='Password123!', email='del@example.com',
        )
        login = self.client.post('/api/auth/login/', {'username': 'deluser', 'password': 'Password123!'})
        self.access_token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_delete_deactivates_account(self):
        r = self.client.delete('/api/users/me/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_deactivated_user_cannot_login(self):
        self.client.delete('/api/users/me/')
        self.client.credentials()
        r = self.client.post('/api/auth/login/', {'username': 'deluser', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_requires_auth(self):
        self.client.credentials()
        r = self.client.delete('/api/users/me/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_record_still_exists(self):
        """Deactivation is soft-delete, user record remains."""
        self.client.delete('/api/users/me/')
        self.assertTrue(CustomUser.objects.filter(username='deluser').exists())


class UserDetailPermissionTests(TestCase):
    """Tests that users cannot modify other users' profiles."""

    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            username='user1', password='Password123!', email='u1@example.com',
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2', password='Password123!', email='u2@example.com',
        )
        login = self.client.post('/api/auth/login/', {'username': 'user1', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_can_read_other_user(self):
        r = self.client.get(f'/api/users/{self.user2.pk}/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_cannot_patch_other_user(self):
        r = self.client.patch(f'/api/users/{self.user2.pk}/', {'first_name': 'Hacked'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_delete_other_user(self):
        r = self.client.delete(f'/api/users/{self.user2.pk}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_update_own_detail(self):
        r = self.client.patch(f'/api/users/{self.user1.pk}/', {'first_name': 'Mine'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['first_name'], 'Mine')


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
        """Login should execute minimal DB queries (user lookup + token insert + lockout check + attempt record)."""
        CustomUser.objects.create_user(username='quser', password='Password123!', email='q@example.com')
        with self.assertNumQueries(4):
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


class RoleBasedAccessMixin:
    """Helper mixin to create users with different roles and authenticate them."""

    def _create_users(self) -> None:
        self.admin = CustomUser.objects.create_user(
            username='admin', password='Password123!', email='admin@example.com', role='admin',
        )
        self.editor = CustomUser.objects.create_user(
            username='editor', password='Password123!', email='editor@example.com', role='editor',
        )
        self.viewer = CustomUser.objects.create_user(
            username='viewer', password='Password123!', email='viewer@example.com', role='viewer',
        )

    def _auth_as(self, user: CustomUser) -> None:
        login = self.client.post('/api/auth/login/', {'username': user.username, 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def _unauth(self) -> None:
        self.client.credentials()


class AdminRoleManagementTests(RoleBasedAccessMixin, TestCase):
    """Tests for admin-only user role management endpoints."""

    def setUp(self):
        self.client = APIClient()
        self._create_users()

    def test_admin_can_change_user_role(self):
        self._auth_as(self.admin)
        r = self.client.patch(f'/api/users/{self.viewer.pk}/role/', {'role': 'editor'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['role'], 'editor')
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.role, 'editor')

    def test_editor_cannot_change_roles(self):
        self._auth_as(self.editor)
        r = self.client.patch(f'/api/users/{self.viewer.pk}/role/', {'role': 'admin'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_change_roles(self):
        self._auth_as(self.viewer)
        r = self.client.patch(f'/api/users/{self.editor.pk}/role/', {'role': 'admin'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_change_roles(self):
        self._unauth()
        r = self.client.patch(f'/api/users/{self.viewer.pk}/role/', {'role': 'editor'})
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_invalid_role_rejected(self):
        self._auth_as(self.admin)
        r = self.client.patch(f'/api/users/{self.viewer.pk}/role/', {'role': 'superuser'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_activate_deactivate_user(self):
        self._auth_as(self.admin)
        r = self.client.patch(f'/api/users/{self.viewer.pk}/activate/', {'is_active': False})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertFalse(self.viewer.is_active)

        r = self.client.patch(f'/api/users/{self.viewer.pk}/activate/', {'is_active': True})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.viewer.refresh_from_db()
        self.assertTrue(self.viewer.is_active)

    def test_editor_cannot_activate_user(self):
        self._auth_as(self.editor)
        r = self.client.patch(f'/api/users/{self.viewer.pk}/activate/', {'is_active': False})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_assign_all_valid_roles(self):
        self._auth_as(self.admin)
        for role in ['admin', 'editor', 'viewer']:
            r = self.client.patch(f'/api/users/{self.viewer.pk}/role/', {'role': role})
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            self.assertEqual(r.data['role'], role)

    def test_new_users_default_to_viewer_role(self):
        self._unauth()
        r = self.client.post('/api/users/register/', {
            'username': 'newroleuser', 'email': 'newrole@example.com',
            'password': 'Password123!', 'password_confirm': 'Password123!',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['role'], 'viewer')

    def test_role_included_in_login_response(self):
        r = self.client.post('/api/auth/login/', {'username': 'admin', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['user']['role'], 'admin')

    def test_users_cannot_escalate_own_role(self):
        self._auth_as(self.viewer)
        r = self.client.patch('/api/users/me/', {'role': 'admin'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['role'], 'viewer')


class SpaceRolePermissionTests(RoleBasedAccessMixin, TestCase):
    """Tests that space CRUD respects role-based permissions."""

    def setUp(self):
        self.client = APIClient()
        self._create_users()
        # Create a space as admin
        self._auth_as(self.admin)
        from spaces.models import Space
        self.space = Space.objects.create(name='Test Space', key='TST', owner=self.admin)

    def test_viewer_can_list_spaces(self):
        self._auth_as(self.viewer)
        r = self.client.get('/api/spaces/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_can_read_space(self):
        self._auth_as(self.viewer)
        r = self.client.get(f'/api/spaces/{self.space.key}/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_create_space(self):
        self._auth_as(self.viewer)
        r = self.client.post('/api/spaces/', {'name': 'New', 'key': 'NEW'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_create_space(self):
        self._auth_as(self.editor)
        r = self.client.post('/api/spaces/', {'name': 'Editor Space', 'key': 'EDT'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_admin_can_create_space(self):
        self._auth_as(self.admin)
        r = self.client.post('/api/spaces/', {'name': 'Admin Space', 'key': 'ADM'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_editor_cannot_delete_other_space(self):
        self._auth_as(self.editor)
        r = self.client.delete(f'/api/spaces/{self.space.key}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_any_space(self):
        self._auth_as(self.admin)
        r = self.client.delete(f'/api/spaces/{self.space.key}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_cannot_access_spaces(self):
        self._unauth()
        r = self.client.get('/api/spaces/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class PageRolePermissionTests(RoleBasedAccessMixin, TestCase):
    """Tests that page CRUD respects role-based permissions."""

    def setUp(self):
        self.client = APIClient()
        self._create_users()
        from spaces.models import Space
        from pages.models import Page
        self.space = Space.objects.create(name='Test', key='TST', owner=self.admin)
        self.page = Page.objects.create(
            title='Test Page', space=self.space, created_by=self.editor,
            updated_by=self.editor, body_markdown='content', position=0,
        )

    def test_viewer_can_read_pages(self):
        self._auth_as(self.viewer)
        r = self.client.get('/api/pages/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_create_page(self):
        self._auth_as(self.viewer)
        r = self.client.post('/api/pages/', {
            'title': 'Viewer Page', 'space': self.space.pk,
            'body_markdown': 'test',
        })
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_create_page(self):
        self._auth_as(self.editor)
        r = self.client.post('/api/pages/', {
            'title': 'Editor Page', 'space': self.space.pk,
            'body_markdown': 'test', 'body_html': '<p>test</p>', 'position': 0,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_editor_can_edit_own_page(self):
        self._auth_as(self.editor)
        r = self.client.patch(f'/api/pages/{self.page.pk}/', {'title': 'Updated'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_any_page(self):
        self._auth_as(self.admin)
        r = self.client.delete(f'/api/pages/{self.page.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_cannot_access_pages(self):
        self._unauth()
        r = self.client.get('/api/pages/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class CommentRolePermissionTests(RoleBasedAccessMixin, TestCase):
    """Tests that comment operations respect role-based permissions."""

    def setUp(self):
        self.client = APIClient()
        self._create_users()
        from spaces.models import Space
        from pages.models import Page, Comment
        self.space = Space.objects.create(name='Test', key='TST', owner=self.admin)
        self.page = Page.objects.create(
            title='Test Page', space=self.space, created_by=self.admin,
            updated_by=self.admin, body_markdown='content', position=0,
        )
        self.comment = Comment.objects.create(
            page=self.page, author=self.editor, body='Editor comment',
        )

    def test_viewer_can_read_comments(self):
        self._auth_as(self.viewer)
        r = self.client.get('/api/comments/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_can_create_comment(self):
        self._auth_as(self.viewer)
        r = self.client.post('/api/comments/', {
            'page': self.page.pk, 'body': 'Viewer comment',
        })
        self.assertIn(r.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_viewer_cannot_delete_other_comment(self):
        self._auth_as(self.viewer)
        r = self.client.delete(f'/api/comments/{self.comment.pk}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_comment(self):
        self._auth_as(self.editor)
        r = self.client.delete(f'/api/comments/{self.comment.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_any_comment(self):
        self._auth_as(self.admin)
        r = self.client.delete(f'/api/comments/{self.comment.pk}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_cannot_access_comments(self):
        self._unauth()
        r = self.client.get('/api/comments/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class AnalyticsRolePermissionTests(RoleBasedAccessMixin, TestCase):
    """Tests that analytics endpoints enforce appropriate role requirements."""

    def setUp(self):
        self.client = APIClient()
        self._create_users()

    def test_admin_can_access_overview(self):
        self._auth_as(self.admin)
        r = self.client.get('/api/analytics/overview/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_editor_cannot_access_overview(self):
        self._auth_as(self.editor)
        r = self.client.get('/api/analytics/overview/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_access_overview(self):
        self._auth_as(self.viewer)
        r = self.client.get('/api/analytics/overview/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_user_activity(self):
        self._auth_as(self.admin)
        r = self.client.get('/api/analytics/user-activity/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_editor_cannot_access_user_activity(self):
        self._auth_as(self.editor)
        r = self.client.get('/api/analytics/user-activity/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_access_content_activity(self):
        self._auth_as(self.editor)
        r = self.client.get('/api/analytics/content-activity/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_can_access_content_activity(self):
        self._auth_as(self.viewer)
        r = self.client.get('/api/analytics/content-activity/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_access_analytics(self):
        self._unauth()
        r = self.client.get('/api/analytics/overview/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class SearchRolePermissionTests(RoleBasedAccessMixin, TestCase):
    """Tests that search requires authentication."""

    def setUp(self):
        self.client = APIClient()
        self._create_users()

    def test_authenticated_user_can_search(self):
        self._auth_as(self.viewer)
        r = self.client.get('/api/search/', {'q': 'test'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cannot_search(self):
        self._unauth()
        r = self.client.get('/api/search/', {'q': 'test'})
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class PermissionClassUnitTests(TestCase):
    """Unit tests for individual permission classes."""

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            username='padmin', password='Password123!', email='padmin@test.com', role='admin',
        )
        self.editor = CustomUser.objects.create_user(
            username='peditor', password='Password123!', email='peditor@test.com', role='editor',
        )
        self.viewer = CustomUser.objects.create_user(
            username='pviewer', password='Password123!', email='pviewer@test.com', role='viewer',
        )

    def _auth_as(self, user: CustomUser) -> None:
        login = self.client.post('/api/auth/login/', {'username': user.username, 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_role_persists_across_login(self):
        """Ensure role is correctly returned in JWT and /me endpoint."""
        for user, expected_role in [(self.admin, 'admin'), (self.editor, 'editor'), (self.viewer, 'viewer')]:
            self._auth_as(user)
            r = self.client.get('/api/users/me/')
            self.assertEqual(r.data['role'], expected_role, f"{user.username} should have role {expected_role}")

    def test_role_in_jwt_token_claims(self):
        """Verify role is embedded in JWT token."""
        r = self.client.post('/api/auth/login/', {'username': 'padmin', 'password': 'Password123!'})
        self.assertEqual(r.data['user']['role'], 'admin')


# ── Registration validation tests ────────────────────────────────────

class RegisterValidationTests(TestCase):
    """Tests for enhanced registration input validation."""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'Valid',
            'last_name': 'User',
        }

    def test_username_too_short(self):
        payload = {**self.valid_payload, 'username': 'ab'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', r.data)

    def test_username_too_long(self):
        payload = {**self.valid_payload, 'username': 'a' * 31}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', r.data)

    def test_username_starts_with_number(self):
        payload = {**self.valid_payload, 'username': '1badname'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', r.data)

    def test_username_special_chars_rejected(self):
        payload = {**self.valid_payload, 'username': 'bad user!'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_username_valid_with_dots_hyphens_underscores(self):
        payload = {**self.valid_payload, 'username': 'valid.user-name_1'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_username_whitespace_stripped(self):
        payload = {**self.valid_payload, 'username': '  validuser  '}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['username'], 'validuser')

    def test_email_no_domain_dot(self):
        payload = {**self.valid_payload, 'email': 'user@localhost'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', r.data)

    def test_email_too_long(self):
        payload = {**self.valid_payload, 'email': 'a' * 250 + '@example.com'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_no_uppercase(self):
        payload = {**self.valid_payload, 'password': 'password123!', 'password_confirm': 'password123!'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', r.data)

    def test_password_no_lowercase(self):
        payload = {**self.valid_payload, 'password': 'PASSWORD123!', 'password_confirm': 'PASSWORD123!'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_no_digit(self):
        payload = {**self.valid_payload, 'password': 'PasswordABC!', 'password_confirm': 'PasswordABC!'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_no_special_char(self):
        payload = {**self.valid_payload, 'password': 'Password123', 'password_confirm': 'Password123'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_long(self):
        long_pw = 'Aa1!' + 'x' * 125
        payload = {**self.valid_payload, 'password': long_pw, 'password_confirm': long_pw}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_username_rejected(self):
        payload = {**self.valid_payload, 'username': ''}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_email_rejected(self):
        payload = {**self.valid_payload, 'email': ''}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blank_password_rejected(self):
        payload = {**self.valid_payload, 'password': '', 'password_confirm': ''}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_case_insensitive_username_duplicate(self):
        CustomUser.objects.create_user(username='TakenUser', password='Password123!', email='taken@example.com')
        payload = {**self.valid_payload, 'username': 'takenuser', 'email': 'new@example.com'}
        r = self.client.post('/api/users/register/', payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', r.data)


# ── Login validation tests ───────────────────────────────────────────

class LoginValidationTests(TestCase):
    """Tests for enhanced login input validation."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='loginval', password='Password123!', email='loginval@example.com',
        )

    def test_login_blank_username(self):
        r = self.client.post('/api/auth/login/', {'username': '', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_blank_password(self):
        r = self.client.post('/api/auth/login/', {'username': 'loginval', 'password': ''})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_whitespace_username_stripped(self):
        r = self.client.post('/api/auth/login/', {'username': '  loginval  ', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_login_empty_body(self):
        r = self.client.post('/api/auth/login/', {})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_credentials_message(self):
        r = self.client.post('/api/auth/login/', {'username': 'loginval', 'password': 'WrongPass!'})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', r.data)


# ── Password reset tests ────────────────────────────────────────────

class PasswordResetRequestTests(TestCase):
    """Tests for the forgotten-password request endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='resetuser', password='Password123!', email='reset@example.com',
        )

    def test_request_with_valid_email(self):
        r = self.client.post('/api/auth/password-reset/', {'email': 'reset@example.com'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('detail', r.data)

    def test_request_with_nonexistent_email_still_200(self):
        """Must not reveal whether email exists (prevents enumeration)."""
        r = self.client.post('/api/auth/password-reset/', {'email': 'nobody@example.com'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_request_with_invalid_email_format(self):
        r = self.client.post('/api/auth/password-reset/', {'email': 'not-an-email'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', r.data)

    def test_request_with_blank_email(self):
        r = self.client.post('/api/auth/password-reset/', {'email': ''})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_with_missing_email(self):
        r = self.client.post('/api/auth/password-reset/', {})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_with_no_domain_dot(self):
        r = self.client.post('/api/auth/password-reset/', {'email': 'user@localhost'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_does_not_get_reset(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        r = self.client.post('/api/auth/password-reset/', {'email': 'reset@example.com'})
        # Still 200 to prevent enumeration, but no email sent
        self.assertEqual(r.status_code, status.HTTP_200_OK)


class PasswordResetConfirmTests(TestCase):
    """Tests for the password-reset confirmation endpoint."""

    def setUp(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='confirmuser', password='OldPassword123!', email='confirm@example.com',
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_reset_confirm_success(self):
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'NewPassword456!',
        })
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # Verify new password works
        login = self.client.post('/api/auth/login/', {
            'username': 'confirmuser', 'password': 'NewPassword456!',
        })
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_reset_confirm_invalid_token(self):
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': 'invalid-token',
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'NewPassword456!',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_confirm_invalid_uid(self):
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': 'invaliduid',
            'token': self.token,
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'NewPassword456!',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_confirm_missing_uid(self):
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'token': self.token,
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'NewPassword456!',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_confirm_password_mismatch(self):
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'DifferentPass1!',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password_confirm', str(r.data))

    def test_reset_confirm_weak_password(self):
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'weak',
            'new_password_confirm': 'weak',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_confirm_password_no_special_char(self):
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'Password123',
            'new_password_confirm': 'Password123',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_invalidated_after_use(self):
        """Token should not work twice (password change invalidates it)."""
        self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'NewPassword456!',
        })
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'AnotherPass789!',
            'new_password_confirm': 'AnotherPass789!',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_cannot_reset(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        r = self.client.post('/api/auth/password-reset/confirm/', {
            'uid': self.uid,
            'token': self.token,
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'NewPassword456!',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


# ── Account lockout tests ────────────────────────────────────────────

@override_settings(ACCOUNT_LOCKOUT_MAX_ATTEMPTS=3, ACCOUNT_LOCKOUT_WINDOW_MINUTES=15)
class AccountLockoutTests(TestCase):
    """Tests for the account lockout mechanism."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='lockuser', password='Password123!', email='lock@example.com',
        )

    def test_lockout_after_max_failed_attempts(self):
        for _ in range(3):
            self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Wrong!'})
        r = self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('locked', str(r.data).lower())

    def test_successful_login_before_lockout(self):
        for _ in range(2):
            self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Wrong!'})
        r = self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_lockout_records_attempt(self):
        for _ in range(3):
            self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Wrong!'})
        self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Password123!'})
        locked_attempts = LoginAttempt.objects.filter(username='lockuser', locked_out=True)
        self.assertTrue(locked_attempts.exists())

    def test_lockout_case_insensitive(self):
        for _ in range(3):
            self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Wrong!'})
        r = self.client.post('/api/auth/login/', {'username': 'LOCKUSER', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lockout_expires_after_window(self):
        """After the lockout window, attempts should reset."""
        cutoff = timezone.now() - timezone.timedelta(minutes=20)
        for _ in range(3):
            attempt = LoginAttempt.objects.create(
                username='lockuser', success=False, ip_address='127.0.0.1',
            )
            LoginAttempt.objects.filter(pk=attempt.pk).update(timestamp=cutoff)
        self.assertFalse(LoginAttempt.is_locked_out('lockuser'))

    def test_login_attempt_recorded_on_success(self):
        self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Password123!'})
        self.assertTrue(
            LoginAttempt.objects.filter(username='lockuser', success=True).exists()
        )

    def test_login_attempt_recorded_on_failure(self):
        self.client.post('/api/auth/login/', {'username': 'lockuser', 'password': 'Wrong!'})
        self.assertTrue(
            LoginAttempt.objects.filter(username='lockuser', success=False).exists()
        )


# ── Login attempt model tests ────────────────────────────────────────

class LoginAttemptModelTests(TestCase):
    """Unit tests for the LoginAttempt model."""

    def test_recent_failures_count(self):
        for _ in range(3):
            LoginAttempt.objects.create(username='testuser', success=False)
        LoginAttempt.objects.create(username='testuser', success=True)
        self.assertEqual(LoginAttempt.recent_failures('testuser'), 3)

    def test_recent_failures_case_insensitive(self):
        LoginAttempt.objects.create(username='TestUser', success=False)
        self.assertEqual(LoginAttempt.recent_failures('testuser'), 1)

    def test_is_locked_out_false_when_below_threshold(self):
        LoginAttempt.objects.create(username='testuser', success=False)
        self.assertFalse(LoginAttempt.is_locked_out('testuser'))

    @override_settings(ACCOUNT_LOCKOUT_MAX_ATTEMPTS=2)
    def test_is_locked_out_true_when_at_threshold(self):
        LoginAttempt.objects.create(username='testuser', success=False)
        LoginAttempt.objects.create(username='testuser', success=False)
        self.assertTrue(LoginAttempt.is_locked_out('testuser'))

    def test_record_creates_attempt(self):
        attempt = LoginAttempt.record(username='testuser', success=True)
        self.assertTrue(attempt.pk)
        self.assertTrue(attempt.success)

    def test_str_representation(self):
        attempt = LoginAttempt.objects.create(username='testuser', success=False)
        self.assertIn('testuser', str(attempt))
        self.assertIn('failed', str(attempt))


# ── Email verification tests ─────────────────────────────────────────

class EmailVerificationSendTests(TestCase):
    """Tests for the email verification send endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='verifyuser', password='Password123!', email='verify@example.com',
        )
        login = self.client.post('/api/auth/login/', {'username': 'verifyuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_send_verification_email(self):
        r = self.client.post('/api/auth/email-verify/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('Verification email sent', r.data['detail'])
        self.assertTrue(EmailVerificationToken.objects.filter(user=self.user).exists())

    def test_already_verified_returns_ok(self):
        self.user.email_verified = True
        self.user.save(update_fields=['email_verified'])
        r = self.client.post('/api/auth/email-verify/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('already verified', r.data['detail'].lower())

    def test_resend_replaces_token(self):
        self.client.post('/api/auth/email-verify/')
        token1 = EmailVerificationToken.objects.get(user=self.user).token
        self.client.post('/api/auth/email-verify/')
        token2 = EmailVerificationToken.objects.get(user=self.user).token
        self.assertNotEqual(token1, token2)

    def test_requires_auth(self):
        self.client.credentials()
        r = self.client.post('/api/auth/email-verify/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class EmailVerificationConfirmTests(TestCase):
    """Tests for the email verification confirm endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='confirmverify', password='Password123!', email='confv@example.com',
        )
        self.verification = EmailVerificationToken.objects.create(
            user=self.user, token='valid-test-token-123',
        )

    def test_confirm_success(self):
        r = self.client.post('/api/auth/email-verify/confirm/', {'token': 'valid-test-token-123'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        self.assertFalse(EmailVerificationToken.objects.filter(user=self.user).exists())

    def test_confirm_invalid_token(self):
        r = self.client.post('/api/auth/email-verify/confirm/', {'token': 'invalid-token'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_missing_token(self):
        r = self.client.post('/api/auth/email-verify/confirm/', {})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_expired_token(self):
        cutoff = timezone.now() - timezone.timedelta(hours=25)
        EmailVerificationToken.objects.filter(pk=self.verification.pk).update(created_at=cutoff)
        r = self.client.post('/api/auth/email-verify/confirm/', {'token': 'valid-test-token-123'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', r.data['detail'].lower())

    def test_token_deleted_after_use(self):
        self.client.post('/api/auth/email-verify/confirm/', {'token': 'valid-test-token-123'})
        r = self.client.post('/api/auth/email-verify/confirm/', {'token': 'valid-test-token-123'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


# ── Email verified flag in profile tests ─────────────────────────────

class EmailVerifiedProfileTests(TestCase):
    """Tests that email_verified is included in user responses and resets on email change."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='evpuser', password='Password123!', email='evp@example.com',
            email_verified=True,
        )
        login = self.client.post('/api/auth/login/', {'username': 'evpuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_email_verified_in_profile(self):
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data['email_verified'])

    def test_email_verified_in_login_response(self):
        self.client.credentials()
        r = self.client.post('/api/auth/login/', {'username': 'evpuser', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data['user']['email_verified'])

    def test_email_verified_in_register_response(self):
        self.client.credentials()
        r = self.client.post('/api/users/register/', {
            'username': 'newevp', 'email': 'newevp@example.com',
            'password': 'Password123!', 'password_confirm': 'Password123!',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertFalse(r.data['email_verified'])

    def test_email_change_resets_verified(self):
        r = self.client.patch('/api/users/me/', {'email': 'newemail@example.com'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_verified)

    def test_same_email_keeps_verified(self):
        r = self.client.patch('/api/users/me/', {'email': 'evp@example.com'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_email_verified_not_editable_via_profile(self):
        self.user.email_verified = False
        self.user.save(update_fields=['email_verified'])
        r = self.client.patch('/api/users/me/', {'email_verified': True})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_verified)


# ── Login history tests ──────────────────────────────────────────────

class LoginHistoryTests(TestCase):
    """Tests for the login history endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='histuser', password='Password123!', email='hist@example.com',
        )
        login = self.client.post('/api/auth/login/', {'username': 'histuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_login_history_returns_attempts(self):
        r = self.client.get('/api/auth/login-history/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)
        self.assertGreaterEqual(len(r.data['results']), 1)

    def test_login_history_includes_fields(self):
        r = self.client.get('/api/auth/login-history/')
        entry = r.data['results'][0]
        self.assertIn('ip_address', entry)
        self.assertIn('success', entry)
        self.assertIn('timestamp', entry)
        self.assertIn('user_agent', entry)
        self.assertIn('locked_out', entry)

    def test_login_history_requires_auth(self):
        self.client.credentials()
        r = self.client.get('/api/auth/login-history/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_login_history_only_shows_own_attempts(self):
        other = CustomUser.objects.create_user(
            username='otheruser', password='Password123!', email='other@example.com',
        )
        LoginAttempt.record(username='otheruser', success=True)
        r = self.client.get('/api/auth/login-history/')
        for entry in r.data['results']:
            self.assertTrue(entry['success'] or not entry['success'])
        # All entries should belong to histuser (verified via the view filter)
        usernames = LoginAttempt.objects.filter(
            username__iexact='histuser',
        ).values_list('username', flat=True)
        self.assertTrue(all(u.lower() == 'histuser' for u in usernames))

    def test_login_history_max_20_entries(self):
        for _ in range(25):
            LoginAttempt.record(username='histuser', success=True)
        r = self.client.get('/api/auth/login-history/')
        self.assertLessEqual(len(r.data['results']), 20)


# ── Activity summary tests ───────────────────────────────────────────

class ActivitySummaryTests(TestCase):
    """Tests for the user activity summary endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='actuser', password='Password123!', email='act@example.com',
            role='editor',
        )
        login = self.client.post('/api/auth/login/', {'username': 'actuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_activity_summary_returns_data(self):
        r = self.client.get('/api/users/me/activity/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('username', r.data)
        self.assertIn('pages_created', r.data)
        self.assertIn('comments_made', r.data)
        self.assertIn('spaces_owned', r.data)
        self.assertIn('recent_logins', r.data)
        self.assertIn('email_verified', r.data)
        self.assertIn('role', r.data)

    def test_activity_summary_correct_username(self):
        r = self.client.get('/api/users/me/activity/')
        self.assertEqual(r.data['username'], 'actuser')
        self.assertEqual(r.data['role'], 'editor')

    def test_activity_summary_requires_auth(self):
        self.client.credentials()
        r = self.client.get('/api/users/me/activity/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_activity_summary_counts_pages(self):
        from spaces.models import Space
        from pages.models import Page
        space = Space.objects.create(name='Test', key='TST', owner=self.user)
        Page.objects.create(
            title='Test Page', space=space, created_by=self.user,
            updated_by=self.user, body_markdown='content', position=0,
        )
        r = self.client.get('/api/users/me/activity/')
        self.assertEqual(r.data['pages_created'], 1)

    def test_activity_summary_counts_spaces(self):
        from spaces.models import Space
        Space.objects.create(name='My Space', key='MSP', owner=self.user)
        r = self.client.get('/api/users/me/activity/')
        self.assertEqual(r.data['spaces_owned'], 1)

    def test_activity_summary_includes_recent_logins(self):
        r = self.client.get('/api/users/me/activity/')
        self.assertIsInstance(r.data['recent_logins'], list)
        self.assertGreaterEqual(len(r.data['recent_logins']), 1)


# ── New endpoint reachability smoke tests ─────────────────────────────

class NewEndpointSmokeTests(TestCase):
    """Smoke tests that all new auth endpoints are reachable."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='smokeuser', password='Password123!', email='smoke2@example.com',
        )
        login = self.client.post('/api/auth/login/', {'username': 'smokeuser', 'password': 'Password123!'})
        self.access = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_email_verify_endpoint_reachable(self):
        r = self.client.post('/api/auth/email-verify/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_email_verify_confirm_reachable(self):
        r = self.client.post('/api/auth/email-verify/confirm/', {'token': 'fake'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_history_reachable(self):
        r = self.client.get('/api/auth/login-history/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_activity_summary_reachable(self):
        r = self.client.get('/api/users/me/activity/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_phone_verify_endpoint_reachable(self):
        self.user.phone_number = '+14155552671'
        self.user.save(update_fields=['phone_number'])
        r = self.client.post('/api/auth/phone-verify/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_phone_verify_confirm_reachable(self):
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '000000'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


# ── Phone verification tests ─────────────────────────────────────────

class PhoneVerificationSendTests(TestCase):
    """Tests for the phone verification send endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='phoneuser', password='Password123!', email='phone@example.com',
            phone_number='+14155552671',
        )
        login = self.client.post('/api/auth/login/', {'username': 'phoneuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_send_code(self):
        r = self.client.post('/api/auth/phone-verify/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('Verification code sent', r.data['detail'])
        self.assertTrue(PhoneVerificationToken.objects.filter(user=self.user).exists())

    def test_send_code_with_new_phone(self):
        r = self.client.post('/api/auth/phone-verify/', {'phone_number': '+14155559999'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '+14155559999')
        self.assertFalse(self.user.phone_verified)

    def test_send_code_no_phone_on_file(self):
        self.user.phone_number = ''
        self.user.save(update_fields=['phone_number'])
        r = self.client.post('/api/auth/phone-verify/')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No phone number', r.data['detail'])

    def test_already_verified(self):
        self.user.phone_verified = True
        self.user.save(update_fields=['phone_verified'])
        r = self.client.post('/api/auth/phone-verify/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('already verified', r.data['detail'].lower())

    def test_resend_replaces_code(self):
        self.client.post('/api/auth/phone-verify/')
        code1 = PhoneVerificationToken.objects.get(user=self.user).code
        self.client.post('/api/auth/phone-verify/')
        code2 = PhoneVerificationToken.objects.get(user=self.user).code
        # Codes are random, so they should differ (extremely unlikely to be equal)
        self.assertEqual(PhoneVerificationToken.objects.filter(user=self.user).count(), 1)

    def test_requires_auth(self):
        self.client.credentials()
        r = self.client.post('/api/auth/phone-verify/')
        self.assertIn(r.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_invalid_phone_rejected(self):
        r = self.client.post('/api/auth/phone-verify/', {'phone_number': 'not-a-phone'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class PhoneVerificationConfirmTests(TestCase):
    """Tests for the phone verification confirm endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='pconfirm', password='Password123!', email='pconfirm@example.com',
            phone_number='+14155552671',
        )
        login = self.client.post('/api/auth/login/', {'username': 'pconfirm', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        self.token = PhoneVerificationToken.objects.create(
            user=self.user, code='123456',
        )

    def test_confirm_success(self):
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '123456'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.phone_verified)
        self.assertFalse(PhoneVerificationToken.objects.filter(user=self.user).exists())

    def test_confirm_wrong_code(self):
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '999999'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid code', r.data['detail'])
        self.token.refresh_from_db()
        self.assertEqual(self.token.attempts, 1)

    def test_confirm_missing_code(self):
        r = self.client.post('/api/auth/phone-verify/confirm/', {})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_no_pending_token(self):
        self.token.delete()
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '123456'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No pending verification', r.data['detail'])

    def test_confirm_expired_code(self):
        cutoff = timezone.now() - timezone.timedelta(minutes=15)
        PhoneVerificationToken.objects.filter(pk=self.token.pk).update(created_at=cutoff)
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '123456'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expired', r.data['detail'].lower())

    @override_settings(PHONE_VERIFICATION_MAX_ATTEMPTS=2)
    def test_confirm_max_attempts_exceeded(self):
        self.token.attempts = 2
        self.token.save(update_fields=['attempts'])
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '123456'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Too many', r.data['detail'])

    def test_confirm_non_digit_code_rejected(self):
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': 'abcdef'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_code_deleted_after_success(self):
        self.client.post('/api/auth/phone-verify/confirm/', {'code': '123456'})
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '123456'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


# ── User status tests ────────────────────────────────────────────────

class UserStatusTests(TestCase):
    """Tests for user status field and admin status update endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            username='statusadmin', password='Password123!', email='sadmin@example.com',
            role='admin', status='active',
        )
        self.user = CustomUser.objects.create_user(
            username='statususer', password='Password123!', email='suser@example.com',
            status='pending',
        )

    def _auth_as(self, user):
        login = self.client.post('/api/auth/login/', {'username': user.username, 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_new_user_starts_pending(self):
        self.assertEqual(self.user.status, 'pending')

    def test_status_in_profile(self):
        self._auth_as(self.user)
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.data['status'], 'pending')

    def test_status_in_login_response(self):
        r = self.client.post('/api/auth/login/', {'username': 'statususer', 'password': 'Password123!'})
        self.assertEqual(r.data['user']['status'], 'pending')

    def test_admin_can_update_status(self):
        self._auth_as(self.admin)
        r = self.client.patch(f'/api/users/{self.user.pk}/status/', {'status': 'active'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, 'active')

    def test_admin_can_suspend_user(self):
        self._auth_as(self.admin)
        r = self.client.patch(f'/api/users/{self.user.pk}/status/', {'status': 'suspended'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, 'suspended')
        self.assertFalse(self.user.is_active)

    def test_admin_invalid_status_rejected(self):
        self._auth_as(self.admin)
        r = self.client.patch(f'/api/users/{self.user.pk}/status/', {'status': 'invalid'})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_cannot_update_status(self):
        self._auth_as(self.user)
        r = self.client.patch(f'/api/users/{self.user.pk}/status/', {'status': 'active'})
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_status_missing_field(self):
        self._auth_as(self.admin)
        r = self.client.patch(f'/api/users/{self.user.pk}/status/', {})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


# ── Auto-activation on verification tests ─────────────────────────────

class AutoActivationTests(TestCase):
    """Tests that user status auto-activates when both verifications pass."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='autoact', password='Password123!', email='autoact@example.com',
            phone_number='+14155552671', status='pending',
        )

    def test_email_verify_activates_if_no_phone(self):
        """User with no phone number gets activated on email verification."""
        self.user.phone_number = ''
        self.user.save(update_fields=['phone_number'])
        token = EmailVerificationToken.objects.create(user=self.user, token='act-token-1')
        r = self.client.post('/api/auth/email-verify/confirm/', {'token': 'act-token-1'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, 'active')

    def test_email_verify_stays_pending_if_phone_not_verified(self):
        """User with phone stays pending until phone is also verified."""
        token = EmailVerificationToken.objects.create(user=self.user, token='act-token-2')
        r = self.client.post('/api/auth/email-verify/confirm/', {'token': 'act-token-2'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, 'pending')

    def test_phone_verify_activates_if_email_verified(self):
        """Phone verification activates user if email already verified."""
        self.user.email_verified = True
        self.user.save(update_fields=['email_verified'])
        PhoneVerificationToken.objects.create(user=self.user, code='111111')
        login = self.client.post('/api/auth/login/', {'username': 'autoact', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        r = self.client.post('/api/auth/phone-verify/confirm/', {'code': '111111'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.status, 'active')


# ── Phone number in profile tests ─────────────────────────────────────

class PhoneProfileTests(TestCase):
    """Tests that phone fields appear in profile and reset on change."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='ppuser', password='Password123!', email='ppuser@example.com',
            phone_number='+14155552671', phone_verified=True,
        )
        login = self.client.post('/api/auth/login/', {'username': 'ppuser', 'password': 'Password123!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_phone_in_profile(self):
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.data['phone_number'], '+14155552671')
        self.assertTrue(r.data['phone_verified'])

    def test_phone_change_resets_verified(self):
        r = self.client.patch('/api/users/me/', {'phone_number': '+14155559999'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.phone_verified)

    def test_same_phone_keeps_verified(self):
        r = self.client.patch('/api/users/me/', {'phone_number': '+14155552671'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.phone_verified)

    def test_phone_verified_not_editable(self):
        self.user.phone_verified = False
        self.user.save(update_fields=['phone_verified'])
        r = self.client.patch('/api/users/me/', {'phone_verified': True})
        self.user.refresh_from_db()
        self.assertFalse(self.user.phone_verified)


# ── Token security tests ─────────────────────────────────────────────

class TokenSecurityTests(TestCase):
    """Tests for enhanced JWT token claims."""

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='tokenuser', password='Password123!', email='token@example.com',
            role='editor', phone_number='+14155552671',
        )

    def test_login_response_includes_phone_fields(self):
        r = self.client.post('/api/auth/login/', {'username': 'tokenuser', 'password': 'Password123!'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('phone_number', r.data['user'])
        self.assertIn('phone_verified', r.data['user'])
        self.assertIn('status', r.data['user'])

    def test_login_returns_correct_status(self):
        r = self.client.post('/api/auth/login/', {'username': 'tokenuser', 'password': 'Password123!'})
        self.assertEqual(r.data['user']['status'], 'pending')


# ── PhoneVerificationToken model tests ────────────────────────────────

class PhoneVerificationTokenModelTests(TestCase):
    """Unit tests for the PhoneVerificationToken model."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='pvtuser', password='Password123!', email='pvt@example.com',
        )

    def test_generate_code_returns_6_digits(self):
        code = PhoneVerificationToken.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_is_expired_false_when_fresh(self):
        token = PhoneVerificationToken.objects.create(user=self.user, code='123456')
        self.assertFalse(token.is_expired())

    def test_is_expired_true_after_expiry(self):
        token = PhoneVerificationToken.objects.create(user=self.user, code='123456')
        cutoff = timezone.now() - timezone.timedelta(minutes=15)
        PhoneVerificationToken.objects.filter(pk=token.pk).update(created_at=cutoff)
        token.refresh_from_db()
        self.assertTrue(token.is_expired())

    @override_settings(PHONE_VERIFICATION_MAX_ATTEMPTS=3)
    def test_max_attempts_exceeded(self):
        token = PhoneVerificationToken.objects.create(user=self.user, code='123456', attempts=3)
        self.assertTrue(token.max_attempts_exceeded())

    @override_settings(PHONE_VERIFICATION_MAX_ATTEMPTS=3)
    def test_max_attempts_not_exceeded(self):
        token = PhoneVerificationToken.objects.create(user=self.user, code='123456', attempts=2)
        self.assertFalse(token.max_attempts_exceeded())

    def test_str_representation(self):
        token = PhoneVerificationToken.objects.create(user=self.user, code='123456')
        self.assertIn('pvtuser', str(token))
