import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from pages.models import Attachment
from tests.factories import PageFactory, UserFactory


@pytest.mark.django_db
def test_upload_attachment(member_client, member_user, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    p = PageFactory(created_by=member_user, updated_by=member_user)
    f = SimpleUploadedFile("hi.txt", b"hello", content_type="text/plain")
    r = member_client.post(f"/api/pages/{p.id}/attachments", {"file": f}, format="multipart")
    assert r.status_code == 201, r.content
    body = r.json()
    assert body["original_filename"] == "hi.txt"
    assert Attachment.objects.filter(page=p).count() == 1


@pytest.mark.django_db
def test_uploader_can_delete_own_attachment(member_client, member_user, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    p = PageFactory(created_by=member_user, updated_by=member_user)
    a = Attachment.objects.create(
        page=p, file=SimpleUploadedFile("x.txt", b"x"),
        original_filename="x.txt", uploaded_by=member_user,
    )
    r = member_client.delete(f"/api/attachments/{a.id}")
    assert r.status_code == 204
    assert not Attachment.objects.filter(pk=a.pk).exists()


@pytest.mark.django_db
def test_member_cannot_delete_others_attachment(member_client, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    other = UserFactory()
    p = PageFactory()
    a = Attachment.objects.create(
        page=p, file=SimpleUploadedFile("x.txt", b"x"),
        original_filename="x.txt", uploaded_by=other,
    )
    r = member_client.delete(f"/api/attachments/{a.id}")
    assert r.status_code == 403
