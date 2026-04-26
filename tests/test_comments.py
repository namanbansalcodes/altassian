import pytest

from pages.models import Comment
from tests.factories import PageFactory, UserFactory


@pytest.mark.django_db
def test_create_comment(member_client, member_user):
    p = PageFactory()
    r = member_client.post(
        f"/api/pages/{p.id}/comments",
        {"body_md": "Looks good"},
        format="json",
    )
    assert r.status_code == 201, r.content
    assert Comment.objects.filter(page=p).count() == 1


@pytest.mark.django_db
def test_threaded_replies(member_client, member_user):
    p = PageFactory()
    parent = Comment.objects.create(page=p, author=member_user, body_md="root")
    r = member_client.post(
        f"/api/pages/{p.id}/comments",
        {"body_md": "reply", "parent": parent.id},
        format="json",
    )
    assert r.status_code == 201
    assert Comment.objects.get(parent=parent).body_md == "reply"


@pytest.mark.django_db
def test_list_comments(member_client, member_user):
    p = PageFactory()
    Comment.objects.create(page=p, author=member_user, body_md="a")
    Comment.objects.create(page=p, author=member_user, body_md="b")
    r = member_client.get(f"/api/pages/{p.id}/comments")
    assert r.status_code == 200
    assert len(r.json()) == 2


@pytest.mark.django_db
def test_author_can_delete_own_comment(member_client, member_user):
    p = PageFactory()
    c = Comment.objects.create(page=p, author=member_user, body_md="own")
    r = member_client.delete(f"/api/comments/{c.id}")
    assert r.status_code == 204
    c.refresh_from_db()
    assert c.deleted_at is not None


@pytest.mark.django_db
def test_member_cannot_delete_others_comment(member_client):
    p = PageFactory()
    other = UserFactory()
    c = Comment.objects.create(page=p, author=other, body_md="other")
    r = member_client.delete(f"/api/comments/{c.id}")
    assert r.status_code == 403


@pytest.mark.django_db
def test_admin_can_delete_any_comment(admin_client):
    p = PageFactory()
    other = UserFactory()
    c = Comment.objects.create(page=p, author=other, body_md="other")
    r = admin_client.delete(f"/api/comments/{c.id}")
    assert r.status_code == 204
