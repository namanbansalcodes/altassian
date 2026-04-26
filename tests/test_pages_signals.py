import pytest

from pages.models import Page, PageVersion
from tests.factories import SpaceFactory, UserFactory


@pytest.fixture
def make_page(db):
    user = UserFactory()
    space = SpaceFactory()

    def _make(**overrides):
        return Page.objects.create(
            space=space, title=overrides.get("title", "T"),
            body_md=overrides.get("body_md", "# h"),
            created_by=user, updated_by=user,
        )

    return _make


@pytest.mark.django_db
def test_html_cache_populated_on_create(make_page):
    p = make_page(body_md="# Title")
    p.refresh_from_db()
    assert "<h1>Title</h1>" in p.body_html_cache


@pytest.mark.django_db
def test_first_save_creates_version_1(make_page):
    p = make_page(body_md="# v1")
    assert p.versions.count() == 1
    assert p.versions.first().version_n == 1
    assert p.versions.first().body_md == "# v1"


@pytest.mark.django_db
def test_body_change_creates_new_version(make_page):
    p = make_page(body_md="# v1")
    p.body_md = "# v2"
    p.save()
    assert p.versions.count() == 2
    assert p.versions.order_by("version_n").last().body_md == "# v2"


@pytest.mark.django_db
def test_no_version_created_when_body_unchanged(make_page):
    p = make_page(body_md="# same")
    p.title = "different title"
    p.save()
    assert p.versions.count() == 1


@pytest.mark.django_db
def test_search_vector_populated(make_page):
    p = make_page(body_md="alpha beta gamma")
    p.refresh_from_db()
    assert p.search_vector is not None
    # Postgres FTS match
    assert Page.objects.filter(search_vector="gamma").filter(pk=p.pk).exists()
