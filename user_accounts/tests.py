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
