import pytest

from tests.factories import PageFactory


@pytest.mark.django_db
def test_versions_listed(member_client, member_user):
    p = PageFactory(body_md="v1", created_by=member_user, updated_by=member_user)
    p.body_md = "v2"; p.save()
    r = member_client.get(f"/api/pages/{p.id}/versions/")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    assert {v["version_n"] for v in body} == {1, 2}


@pytest.mark.django_db
def test_get_one_version(member_client, member_user):
    p = PageFactory(body_md="v1", created_by=member_user, updated_by=member_user)
    p.body_md = "v2"; p.save()
    r = member_client.get(f"/api/pages/{p.id}/versions/1/")
    assert r.status_code == 200
    assert r.json()["body_md"] == "v1"


@pytest.mark.django_db
def test_restore_version_creates_new_version_with_old_body(member_client, member_user):
    p = PageFactory(body_md="v1", created_by=member_user, updated_by=member_user)
    p.body_md = "v2"; p.save()
    r = member_client.post(f"/api/pages/{p.id}/restore/1/")
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.body_md == "v1"
    assert p.versions.count() == 3   # v1, v2, then v3 = restore of v1
