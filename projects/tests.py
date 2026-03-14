from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from projects.models import Project, Task

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="owner", email="owner@test.com", password="Test1234!", role="editor"
        )

    def test_str(self) -> None:
        project = Project.objects.create(name="My Project", key="MP", owner=self.user)
        self.assertEqual(str(project), "MP - My Project")


class TaskModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="owner", email="owner@test.com", password="Test1234!", role="editor"
        )
        self.project = Project.objects.create(name="P", key="P1", owner=self.user)

    def test_str(self) -> None:
        task = Task.objects.create(
            project=self.project, title="Fix bug", reporter=self.user
        )
        self.assertEqual(str(task), "Fix bug")


class ProjectAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.editor = User.objects.create_user(
            username="editor", email="e@test.com", password="Test1234!", role="editor"
        )
        self.viewer = User.objects.create_user(
            username="viewer", email="v@test.com", password="Test1234!", role="viewer"
        )
        self.admin = User.objects.create_user(
            username="admin", email="a@test.com", password="Test1234!", role="admin"
        )

    def test_create_project(self) -> None:
        self.client.force_authenticate(self.editor)
        resp = self.client.post("/api/projects/", {"name": "Test", "key": "TST"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["owner_username"], "editor")

    def test_viewer_cannot_create(self) -> None:
        self.client.force_authenticate(self.viewer)
        resp = self.client.post("/api/projects/", {"name": "Test", "key": "TST"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_projects(self) -> None:
        Project.objects.create(name="P1", key="P1", owner=self.editor)
        self.client.force_authenticate(self.viewer)
        resp = self.client.get("/api/projects/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_retrieve_project_shows_members(self) -> None:
        p = Project.objects.create(name="P1", key="P1", owner=self.editor)
        p.members.add(self.editor)
        self.client.force_authenticate(self.editor)
        resp = self.client.get("/api/projects/P1/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("members", resp.data)

    def test_add_member(self) -> None:
        p = Project.objects.create(name="P1", key="P1", owner=self.editor)
        self.client.force_authenticate(self.editor)
        resp = self.client.post(
            "/api/projects/P1/add-member/", {"user_id": self.viewer.pk}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(self.viewer, p.members.all())

    def test_remove_owner_fails(self) -> None:
        p = Project.objects.create(name="P1", key="P1", owner=self.editor)
        p.members.add(self.editor)
        self.client.force_authenticate(self.editor)
        resp = self.client.post(
            "/api/projects/P1/remove-member/", {"user_id": self.editor.pk}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_update(self) -> None:
        Project.objects.create(name="P1", key="P1", owner=self.editor)
        self.client.force_authenticate(self.editor)
        resp = self.client.patch("/api/projects/P1/", {"name": "Updated"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "Updated")

    def test_non_owner_editor_cannot_update(self) -> None:
        Project.objects.create(name="P1", key="P1", owner=self.admin)
        other_editor = User.objects.create_user(
            username="ed2", email="ed2@test.com", password="Test1234!", role="editor"
        )
        self.client.force_authenticate(other_editor)
        resp = self.client.patch("/api/projects/P1/", {"name": "Hacked"})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any(self) -> None:
        Project.objects.create(name="P1", key="P1", owner=self.editor)
        self.client.force_authenticate(self.admin)
        resp = self.client.patch("/api/projects/P1/", {"name": "Admin Updated"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class TaskAPITest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.editor = User.objects.create_user(
            username="editor", email="e@test.com", password="Test1234!", role="editor"
        )
        self.viewer = User.objects.create_user(
            username="viewer", email="v@test.com", password="Test1234!", role="viewer"
        )
        self.project = Project.objects.create(
            name="Project", key="PRJ", owner=self.editor
        )

    def test_create_task(self) -> None:
        self.client.force_authenticate(self.editor)
        resp = self.client.post(
            "/api/tasks/",
            {"project": self.project.pk, "title": "Do something"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["reporter_username"], "editor")

    def test_viewer_cannot_create_task(self) -> None:
        self.client.force_authenticate(self.viewer)
        resp = self.client.post(
            "/api/tasks/",
            {"project": self.project.pk, "title": "Nope"},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_project_key(self) -> None:
        Task.objects.create(
            project=self.project, title="T1", reporter=self.editor
        )
        self.client.force_authenticate(self.editor)
        resp = self.client.get("/api/tasks/?project_key=PRJ")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_assign_task(self) -> None:
        task = Task.objects.create(
            project=self.project, title="T1", reporter=self.editor
        )
        self.client.force_authenticate(self.editor)
        resp = self.client.patch(
            f"/api/tasks/{task.pk}/assign/",
            {"assignee_id": self.viewer.pk},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["assignee"], self.viewer.pk)

    def test_unassign_task(self) -> None:
        task = Task.objects.create(
            project=self.project,
            title="T1",
            reporter=self.editor,
            assignee=self.viewer,
        )
        self.client.force_authenticate(self.editor)
        resp = self.client.patch(f"/api/tasks/{task.pk}/assign/", {})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_tasks(self) -> None:
        Task.objects.create(
            project=self.project, title="T1", reporter=self.editor
        )
        self.client.force_authenticate(self.viewer)
        resp = self.client.get("/api/tasks/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_filter_by_status(self) -> None:
        Task.objects.create(
            project=self.project, title="T1", reporter=self.editor, status="todo"
        )
        Task.objects.create(
            project=self.project, title="T2", reporter=self.editor, status="done"
        )
        self.client.force_authenticate(self.editor)
        resp = self.client.get("/api/tasks/?status=done")
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["title"], "T2")
