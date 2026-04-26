import pytest
from rest_framework.test import APIClient

from tests.factories import AdminFactory, OrganizationFactory, UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organization(db):
    return OrganizationFactory()


@pytest.fixture
def admin_user(db, organization):
    return AdminFactory()


@pytest.fixture
def member_user(db, organization):
    return UserFactory()


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def member_client(api_client, member_user):
    api_client.force_authenticate(user=member_user)
    return api_client
