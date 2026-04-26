import pytest
from django.core import mail
from django.utils import timezone

from user_accounts.invite_models import Invite


@pytest.mark.django_db
def test_admin_can_create_invite_and_email_is_sent(admin_client, organization):
    mail.outbox.clear()
    r = admin_client.post("/api/invites", {"email": "new@example.com"}, format="json")
    assert r.status_code == 201, r.content
    body = r.json()
    assert body["email"] == "new@example.com"
    assert "token" not in body  # token never returned to admin

    invite = Invite.objects.get(email="new@example.com")
    assert invite.is_valid()
    assert len(mail.outbox) == 1
    assert "new@example.com" in mail.outbox[0].to
    assert invite.token in mail.outbox[0].body


@pytest.mark.django_db
def test_member_cannot_create_invite(member_client):
    r = member_client.post("/api/invites", {"email": "x@example.com"}, format="json")
    assert r.status_code == 403


@pytest.mark.django_db
def test_admin_lists_invites(admin_client, admin_user):
    Invite.objects.create(email="a@example.com", invited_by=admin_user)
    Invite.objects.create(email="b@example.com", invited_by=admin_user)
    r = admin_client.get("/api/invites")
    assert r.status_code == 200
    assert len(r.json()["results"]) == 2


@pytest.mark.django_db
def test_admin_revokes_invite(admin_client, admin_user):
    inv = Invite.objects.create(email="x@example.com", invited_by=admin_user)
    r = admin_client.delete(f"/api/invites/{inv.id}")
    assert r.status_code == 204
    assert not Invite.objects.filter(pk=inv.pk).exists()


@pytest.mark.django_db
def test_get_invite_by_token_public(api_client, admin_user):
    inv = Invite.objects.create(email="z@example.com", invited_by=admin_user)
    r = api_client.get(f"/api/invites/by-token/{inv.token}")
    assert r.status_code == 200
    assert r.json()["email"] == "z@example.com"


@pytest.mark.django_db
def test_get_invite_by_token_expired(api_client, admin_user):
    from datetime import timedelta
    inv = Invite.objects.create(email="z@example.com", invited_by=admin_user)
    inv.expires_at = timezone.now() - timedelta(days=1)
    inv.save(update_fields=["expires_at"])
    r = api_client.get(f"/api/invites/by-token/{inv.token}")
    assert r.status_code == 410  # Gone


@pytest.mark.django_db
def test_accept_invite_creates_user_and_logs_in(api_client, admin_user):
    inv = Invite.objects.create(email="newuser@example.com", invited_by=admin_user)
    r = api_client.post(
        f"/api/invites/by-token/{inv.token}/accept",
        {"password": "newuserpass123", "display_name": "New User"},
        format="json",
    )
    assert r.status_code == 200, r.content
    from user_accounts.authentication import ACCESS_COOKIE
    assert ACCESS_COOKIE in r.cookies
    inv.refresh_from_db()
    assert inv.accepted_at is not None
    from django.contrib.auth import get_user_model
    User = get_user_model()
    u = User.objects.get(email="newuser@example.com")
    assert u.check_password("newuserpass123")
    assert u.role == User.Role.MEMBER


@pytest.mark.django_db
def test_accept_invite_rejected_if_already_accepted(api_client, admin_user):
    inv = Invite.objects.create(email="x@example.com", invited_by=admin_user, accepted_at=timezone.now())
    r = api_client.post(
        f"/api/invites/by-token/{inv.token}/accept",
        {"password": "p", "display_name": "x"},
        format="json",
    )
    assert r.status_code == 410


@pytest.mark.django_db
def test_invite_existing_user_email_rejected(admin_client, member_user):
    r = admin_client.post("/api/invites", {"email": member_user.email}, format="json")
    assert r.status_code == 400
    assert "already exists" in str(r.json())


@pytest.mark.django_db
def test_invite_existing_user_email_case_insensitive(admin_client):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.create_user(email="bob@example.com", password="x", display_name="Bob")
    r = admin_client.post("/api/invites", {"email": "BOB@EXAMPLE.COM"}, format="json")
    assert r.status_code == 400
