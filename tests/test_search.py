import pytest

from tests.factories import PageFactory, SpaceFactory


@pytest.mark.django_db
def test_search_returns_pages_matching_body(member_client, member_user):
    s1 = SpaceFactory()
    PageFactory(space=s1, title="Auth design", body_md="JWT cookies are great", created_by=member_user, updated_by=member_user)
    PageFactory(space=s1, title="Random", body_md="apples and bananas", created_by=member_user, updated_by=member_user)
    r = member_client.get("/api/search/?q=jwt")
    assert r.status_code == 200
    titles = [p["title"] for p in r.json()["results"]]
    assert titles == ["Auth design"]


@pytest.mark.django_db
def test_search_results_include_snippet_and_rank(member_client, member_user):
    s = SpaceFactory()
    PageFactory(space=s, title="Auth", body_md="JWT cookie security", created_by=member_user, updated_by=member_user)
    r = member_client.get("/api/search/?q=cookie")
    res = r.json()["results"][0]
    assert "snippet_html" in res
    assert "rank" in res
    assert "<b>" in res["snippet_html"] or "cookie" in res["snippet_html"].lower()


@pytest.mark.django_db
def test_search_filters_by_space(member_client, member_user):
    s1 = SpaceFactory(slug="eng")
    s2 = SpaceFactory(slug="prod")
    PageFactory(space=s1, title="A", body_md="alpha thing", created_by=member_user, updated_by=member_user)
    PageFactory(space=s2, title="B", body_md="alpha thing", created_by=member_user, updated_by=member_user)
    r = member_client.get("/api/search/?q=alpha&space=eng")
    titles = {p["title"] for p in r.json()["results"]}
    assert titles == {"A"}


@pytest.mark.django_db
def test_search_excludes_deleted_pages(member_client, member_user):
    from pages.models import Page
    from django.utils import timezone
    s = SpaceFactory()
    p = PageFactory(space=s, title="findme", body_md="alpha", created_by=member_user, updated_by=member_user)
    Page.objects.filter(pk=p.pk).update(deleted_at=timezone.now())
    r = member_client.get("/api/search/?q=alpha")
    assert r.json()["results"] == []


@pytest.mark.django_db
def test_search_unauthed_rejected(api_client):
    r = api_client.get("/api/search/?q=x")
    assert r.status_code == 401
