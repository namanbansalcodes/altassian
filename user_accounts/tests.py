from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

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
        t = self.client.post('/api/auth/login/', {'username': 'charlie', 'password': 'Password123!'})
        self.assertEqual(t.status_code, status.HTTP_200_OK)
        access = t.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        me = self.client.get('/api/users/me/')
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data['username'], 'charlie')
