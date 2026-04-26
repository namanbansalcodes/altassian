import pytest

from tests.factories import PageFactory, SpaceFactory


@pytest.mark.django_db
def test_public_page_readable_unauthed(api_client):
    s = SpaceFactory(slug="docs")
    p = PageFactory(space=s, title="Public", body_md="# Hello", is_public=True)
    r = api_client.get(f"/api/public/spaces/{s.slug}/pages/{p.slug}")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Public"
    assert "<h1>Hello</h1>" in body["body_html"]


@pytest.mark.django_db
def test_private_page_returns_404_on_public_endpoint(api_client):
    s = SpaceFactory(slug="docs")
    p = PageFactory(space=s, is_public=False)
    r = api_client.get(f"/api/public/spaces/{s.slug}/pages/{p.slug}")
    assert r.status_code == 404


@pytest.mark.django_db
def test_deleted_public_page_returns_404(api_client):
    from pages.models import Page
    from django.utils import timezone
    s = SpaceFactory(slug="docs")
    p = PageFactory(space=s, is_public=True)
    Page.objects.filter(pk=p.pk).update(deleted_at=timezone.now())
    r = api_client.get(f"/api/public/spaces/{s.slug}/pages/{p.slug}")
    assert r.status_code == 404
