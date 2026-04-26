import pytest

from user_accounts.authentication import ACCESS_COOKIE, REFRESH_COOKIE


@pytest.mark.django_db
def test_login_sets_access_and_refresh_cookies(api_client, member_user):
    r = api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    assert r.status_code == 200, r.content
    assert ACCESS_COOKIE in r.cookies
    assert REFRESH_COOKIE in r.cookies
    assert r.cookies[ACCESS_COOKIE]["httponly"]
    assert r.cookies[REFRESH_COOKIE]["httponly"]


@pytest.mark.django_db
def test_login_wrong_password_returns_401(api_client, member_user):
    r = api_client.post("/api/auth/login", {"email": member_user.email, "password": "wrong"}, format="json")
    assert r.status_code == 401


@pytest.mark.django_db
def test_login_unknown_email_returns_401(api_client):
    r = api_client.post("/api/auth/login", {"email": "noone@example.com", "password": "x"}, format="json")
    assert r.status_code == 401


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    r = api_client.get("/api/auth/me")
    assert r.status_code == 401


@pytest.mark.django_db
def test_me_returns_user_after_login(api_client, member_user):
    api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    r = api_client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == member_user.email


@pytest.mark.django_db
def test_logout_clears_cookies(api_client, member_user):
    api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    r = api_client.post("/api/auth/logout")
    assert r.status_code == 204
    assert r.cookies[ACCESS_COOKIE].value == ""
    assert r.cookies[REFRESH_COOKIE].value == ""


@pytest.mark.django_db
def test_refresh_rotates_access_cookie(api_client, member_user):
    api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    old_access = api_client.cookies[ACCESS_COOKIE].value
    r = api_client.post("/api/auth/refresh")
    assert r.status_code == 200
    assert r.cookies[ACCESS_COOKIE].value
    assert r.cookies[ACCESS_COOKIE].value != old_access
