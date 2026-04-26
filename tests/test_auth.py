import pytest
from django.core import mail

from user_accounts.authentication import ACCESS_COOKIE, REFRESH_COOKIE
from user_accounts.otp_models import OneTimeCode


def _request_otp(api_client, email):
    """Trigger an OTP and return the plaintext code."""
    mail.outbox.clear()
    r = api_client.post("/api/auth/otp/request", {"email": email}, format="json")
    assert r.status_code == 200, r.content
    assert len(mail.outbox) == 1
    body = mail.outbox[0].body
    # Extract the 6-digit code from the email body.
    import re
    m = re.search(r"\b(\d{6})\b", body)
    assert m, body
    return m.group(1)


@pytest.mark.django_db
def test_otp_request_sends_email_and_creates_record(api_client):
    code = _request_otp(api_client, "newcomer@example.com")
    assert OneTimeCode.objects.filter(email="newcomer@example.com").count() == 1
    assert len(code) == 6


@pytest.mark.django_db
def test_otp_request_response_does_not_leak_code(api_client):
    mail.outbox.clear()
    r = api_client.post("/api/auth/otp/request", {"email": "x@example.com"}, format="json")
    assert r.status_code == 200
    body_text = r.content.decode()
    # No 6-digit code should appear in the JSON response body.
    import re
    assert not re.search(r"\b\d{6}\b", body_text)


@pytest.mark.django_db
def test_otp_verify_unknown_email_rejected(api_client):
    """Public signup is closed — verify returns 403 for any email without an account."""
    code = _request_otp(api_client, "stranger@example.com")
    r = api_client.post(
        "/api/auth/otp/verify",
        {"email": "stranger@example.com", "code": code, "display_name": "Stranger"},
        format="json",
    )
    assert r.status_code == 403, r.content
    assert ACCESS_COOKIE not in r.cookies


@pytest.mark.django_db
def test_otp_verify_existing_user_logs_in(api_client, member_user):
    code = _request_otp(api_client, member_user.email)
    r = api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    assert r.status_code == 200
    assert r.json()["email"] == member_user.email
    assert ACCESS_COOKIE in r.cookies


@pytest.mark.django_db
def test_otp_verify_wrong_code_rejected(api_client, member_user):
    _request_otp(api_client, member_user.email)
    r = api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": "000000"},
        format="json",
    )
    assert r.status_code == 400
    assert ACCESS_COOKIE not in r.cookies


@pytest.mark.django_db
def test_otp_code_single_use(api_client, member_user):
    code = _request_otp(api_client, member_user.email)
    r1 = api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    assert r1.status_code == 200
    # Second verify with the same code must fail.
    api_client.cookies.clear()
    r2 = api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    assert r2.status_code == 400


@pytest.mark.django_db
def test_otp_code_expires(api_client, member_user):
    from datetime import timedelta
    from django.utils import timezone

    code = _request_otp(api_client, member_user.email)
    otp = OneTimeCode.objects.get(email=member_user.email)
    otp.expires_at = timezone.now() - timedelta(minutes=1)
    otp.save(update_fields=["expires_at"])

    r = api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    assert r.status_code == 400


@pytest.mark.django_db
def test_otp_verify_inactive_user_rejected(api_client, member_user):
    member_user.is_active = False
    member_user.save(update_fields=["is_active"])
    code = _request_otp(api_client, member_user.email)
    r = api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    assert r.status_code == 403


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    r = api_client.get("/api/auth/me")
    assert r.status_code == 401


@pytest.mark.django_db
def test_me_returns_user_after_otp_login(api_client, member_user):
    code = _request_otp(api_client, member_user.email)
    api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    r = api_client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == member_user.email


@pytest.mark.django_db
def test_logout_clears_cookies(api_client, member_user):
    code = _request_otp(api_client, member_user.email)
    api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    r = api_client.post("/api/auth/logout")
    assert r.status_code == 204
    assert r.cookies[ACCESS_COOKIE].value == ""
    assert r.cookies[REFRESH_COOKIE].value == ""


@pytest.mark.django_db
def test_refresh_rotates_access_cookie(api_client, member_user):
    code = _request_otp(api_client, member_user.email)
    api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    old_access = api_client.cookies[ACCESS_COOKIE].value
    r = api_client.post("/api/auth/refresh")
    assert r.status_code == 200
    assert r.cookies[ACCESS_COOKIE].value
    assert r.cookies[ACCESS_COOKIE].value != old_access


@pytest.mark.django_db
def test_refresh_rejects_inactive_user(api_client, member_user):
    code = _request_otp(api_client, member_user.email)
    api_client.post(
        "/api/auth/otp/verify",
        {"email": member_user.email, "code": code},
        format="json",
    )
    member_user.is_active = False
    member_user.save(update_fields=["is_active"])
    r = api_client.post("/api/auth/refresh")
    assert r.status_code == 401
