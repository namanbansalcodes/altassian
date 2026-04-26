import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from user_accounts.models import Organization

User = get_user_model()


@pytest.mark.django_db
def test_create_admin_creates_org_and_admin():
    call_command("create_admin", "--email=naman@example.com", "--password=secret123", "--org-name=Altassian")

    assert Organization.objects.count() == 1
    assert Organization.objects.first().name == "Altassian"

    admin = User.objects.get(email="naman@example.com")
    assert admin.is_admin
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.check_password("secret123")


@pytest.mark.django_db
def test_create_admin_idempotent_on_org_but_errors_on_existing_email():
    call_command("create_admin", "--email=naman@example.com", "--password=secret123", "--org-name=Altassian")
    with pytest.raises(SystemExit):
        call_command("create_admin", "--email=naman@example.com", "--password=other", "--org-name=Altassian")
