import pytest


@pytest.mark.django_db
def test_health_check_returns_ok(api_client):
    r = api_client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
