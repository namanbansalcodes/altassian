import pytest

from spaces.models import Space
from tests.factories import SpaceFactory


@pytest.mark.django_db
def test_admin_creates_space(admin_client):
    r = admin_client.post(
        "/api/spaces/",
        {"slug": "eng", "name": "Engineering", "description": "All things engineering"},
        format="json",
    )
    assert r.status_code == 201, r.content
    assert Space.objects.filter(slug="eng").exists()


@pytest.mark.django_db
def test_member_cannot_create_space(member_client):
    r = member_client.post("/api/spaces/", {"slug": "x", "name": "X"}, format="json")
    assert r.status_code == 403


@pytest.mark.django_db
def test_anyone_authed_lists_spaces(member_client):
    SpaceFactory(slug="eng", name="Eng")
    SpaceFactory(slug="prod", name="Prod")
    r = member_client.get("/api/spaces/")
    assert r.status_code == 200
    slugs = {s["slug"] for s in r.json()["results"]}
    assert slugs == {"eng", "prod"}


@pytest.mark.django_db
def test_unauthed_cannot_list_spaces(api_client):
    r = api_client.get("/api/spaces/")
    assert r.status_code == 401


@pytest.mark.django_db
def test_space_detail_includes_page_tree_field(member_client):
    s = SpaceFactory(slug="eng")
    r = member_client.get(f"/api/spaces/{s.slug}/")
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == "eng"
    assert "pages" in body  # tree present (empty list at this point)


@pytest.mark.django_db
def test_admin_updates_space(admin_client):
    s = SpaceFactory(slug="eng", name="Old")
    r = admin_client.patch(f"/api/spaces/{s.slug}/", {"name": "New"}, format="json")
    assert r.status_code == 200
    s.refresh_from_db()
    assert s.name == "New"


@pytest.mark.django_db
def test_admin_deletes_space(admin_client):
    s = SpaceFactory(slug="eng")
    r = admin_client.delete(f"/api/spaces/{s.slug}/")
    assert r.status_code == 204
    assert not Space.objects.filter(slug="eng").exists()
