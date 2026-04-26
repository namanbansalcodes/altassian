import pytest

from pages.models import Page
from tests.factories import PageFactory, SpaceFactory, UserFactory


@pytest.mark.django_db
def test_member_creates_page(member_client, member_user):
    s = SpaceFactory(slug="eng")
    r = member_client.post(
        "/api/pages/",
        {"space": s.id, "title": "Hello", "body_md": "# Hi"},
        format="json",
    )
    assert r.status_code == 201, r.content
    body = r.json()
    assert body["title"] == "Hello"
    assert "<h1>Hi</h1>" in body["body_html"]
    assert body["slug"] == "hello"


@pytest.mark.django_db
def test_unauthed_cannot_create_page(api_client):
    s = SpaceFactory()
    r = api_client.post("/api/pages/", {"space": s.id, "title": "x", "body_md": "x"}, format="json")
    assert r.status_code == 401


@pytest.mark.django_db
def test_page_detail_returns_md_and_html(member_client):
    p = PageFactory(title="T", body_md="# X")
    r = member_client.get(f"/api/pages/{p.id}/")
    assert r.status_code == 200
    body = r.json()
    assert body["body_md"] == "# X"
    assert "<h1>X</h1>" in body["body_html"]


@pytest.mark.django_db
def test_update_page_changes_body_and_creates_version(member_client, member_user):
    p = PageFactory(body_md="# v1", created_by=member_user, updated_by=member_user)
    r = member_client.patch(f"/api/pages/{p.id}/", {"body_md": "# v2"}, format="json")
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.body_md == "# v2"
    assert p.versions.count() == 2


@pytest.mark.django_db
def test_soft_delete_page(member_client, member_user):
    p = PageFactory(created_by=member_user, updated_by=member_user)
    r = member_client.delete(f"/api/pages/{p.id}/")
    assert r.status_code == 204
    p.refresh_from_db()
    assert p.deleted_at is not None


@pytest.mark.django_db
def test_deleted_pages_excluded_from_list(member_client, member_user):
    from django.utils import timezone
    s = SpaceFactory()
    PageFactory(space=s, title="alive", created_by=member_user, updated_by=member_user)
    dead = PageFactory(space=s, title="dead", created_by=member_user, updated_by=member_user)
    Page.objects.filter(pk=dead.pk).update(deleted_at=timezone.now())
    r = member_client.get(f"/api/spaces/{s.slug}/")
    titles = [p["title"] for p in r.json()["pages"]]
    assert "alive" in titles
    assert "dead" not in titles


@pytest.mark.django_db
def test_move_page_changes_parent_and_position(member_client, member_user):
    s = SpaceFactory()
    parent = PageFactory(space=s, created_by=member_user, updated_by=member_user)
    child = PageFactory(space=s, created_by=member_user, updated_by=member_user)
    r = member_client.post(
        f"/api/pages/{child.id}/move/",
        {"parent_id": parent.id, "position": 0},
        format="json",
    )
    assert r.status_code == 200
    child.refresh_from_db()
    assert child.parent_id == parent.id
    assert child.position == 0


@pytest.mark.django_db
def test_page_tree_nested_in_space_detail(member_client, member_user):
    s = SpaceFactory()
    root = PageFactory(space=s, title="Root", created_by=member_user, updated_by=member_user)
    PageFactory(space=s, title="Child", parent=root, created_by=member_user, updated_by=member_user)
    r = member_client.get(f"/api/spaces/{s.slug}/")
    assert r.status_code == 200
    pages = r.json()["pages"]
    assert len(pages) == 1
    assert pages[0]["title"] == "Root"
    assert len(pages[0]["children"]) == 1
    assert pages[0]["children"][0]["title"] == "Child"


@pytest.mark.django_db
def test_member_can_edit_page_authored_by_other_member(api_client, member_user):
    other = UserFactory()
    p = PageFactory(body_md="# original", created_by=other, updated_by=other)
    api_client.force_authenticate(user=member_user)
    r = api_client.patch(f"/api/pages/{p.id}/", {"body_md": "# edited by other"}, format="json")
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.body_md == "# edited by other"


@pytest.mark.django_db
def test_member_cannot_make_page_public(member_client, member_user):
    p = PageFactory(is_public=False, created_by=member_user, updated_by=member_user)
    r = member_client.patch(f"/api/pages/{p.id}/", {"is_public": True}, format="json")
    assert r.status_code == 400
    p.refresh_from_db()
    assert p.is_public is False


@pytest.mark.django_db
def test_admin_can_make_page_public(admin_client, admin_user):
    p = PageFactory(is_public=False, created_by=admin_user, updated_by=admin_user)
    r = admin_client.patch(f"/api/pages/{p.id}/", {"is_public": True}, format="json")
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.is_public is True


@pytest.mark.django_db
def test_member_can_patch_other_fields_without_touching_is_public(member_client, member_user):
    p = PageFactory(is_public=False, body_md="# a", created_by=member_user, updated_by=member_user)
    r = member_client.patch(f"/api/pages/{p.id}/", {"body_md": "# b"}, format="json")
    assert r.status_code == 200
