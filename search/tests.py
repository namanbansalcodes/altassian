from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user_accounts.models import CustomUser
from spaces.models import Space
from pages.models import Page, Comment


class UnifiedSearchViewTests(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = CustomUser.objects.create_user(
            username='searcher', email='searcher@test.com', password='testpass123'
        )
        cls.space = Space.objects.create(
            name='Engineering', key='ENG', description='Engineering docs', owner=cls.user
        )
        cls.space_archived = Space.objects.create(
            name='Old Archive', key='OLD', description='Archived space',
            owner=cls.user, is_archived=True,
        )
        cls.page1 = Page.objects.create(
            title='Getting Started Guide',
            space=cls.space, body_markdown='Welcome to the getting started guide.',
            body_html='<p>Welcome</p>', created_by=cls.user, updated_by=cls.user,
            position=0, is_draft=False,
        )
        cls.page_draft = Page.objects.create(
            title='Draft Architecture Plan',
            space=cls.space, body_markdown='This is a draft about architecture.',
            body_html='<p>Draft</p>', created_by=cls.user, updated_by=cls.user,
            position=1, is_draft=True,
        )
        cls.page_archived = Page.objects.create(
            title='Archived Legacy Docs',
            space=cls.space_archived, body_markdown='Legacy documentation.',
            body_html='<p>Legacy</p>', created_by=cls.user, updated_by=cls.user,
            position=0, is_draft=False,
        )
        cls.comment = Comment.objects.create(
            page=cls.page1, author=cls.user,
            body='This guide is really helpful for getting started!',
        )
        cls.url = reverse('unified-search')

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_search_requires_query(self) -> None:
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('q query param is required', resp.data['detail'])

    def test_search_empty_query(self) -> None:
        resp = self.client.get(self.url, {'q': '  '})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_returns_all_types(self) -> None:
        resp = self.client.get(self.url, {'q': 'getting'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data
        self.assertEqual(data['query'], 'getting')
        self.assertGreaterEqual(data['pages_count'], 1)
        self.assertGreaterEqual(data['comments_count'], 1)
        self.assertIn('spaces', data)
        self.assertIn('comments', data)

    def test_search_pages_by_title(self) -> None:
        resp = self.client.get(self.url, {'q': 'Getting Started', 'type': 'page'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['pages_count'], 1)
        self.assertEqual(resp.data['pages'][0]['title'], 'Getting Started Guide')
        self.assertEqual(resp.data['pages'][0]['result_type'], 'page')

    def test_search_pages_by_body(self) -> None:
        resp = self.client.get(self.url, {'q': 'architecture', 'type': 'page'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['pages_count'], 1)
        self.assertEqual(resp.data['pages'][0]['title'], 'Draft Architecture Plan')

    def test_search_spaces(self) -> None:
        resp = self.client.get(self.url, {'q': 'Engineering', 'type': 'space'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['spaces_count'], 1)
        self.assertEqual(resp.data['spaces'][0]['result_type'], 'space')
        self.assertEqual(resp.data['spaces'][0]['name'], 'Engineering')

    def test_search_spaces_by_key(self) -> None:
        resp = self.client.get(self.url, {'q': 'ENG', 'type': 'space'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['spaces_count'], 1)

    def test_search_comments(self) -> None:
        resp = self.client.get(self.url, {'q': 'helpful', 'type': 'comment'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['comments_count'], 1)
        self.assertEqual(resp.data['comments'][0]['result_type'], 'comment')

    def test_filter_by_type_page_only(self) -> None:
        resp = self.client.get(self.url, {'q': 'getting', 'type': 'page'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['spaces'], [])
        self.assertEqual(resp.data['comments'], [])

    def test_filter_by_type_multiple(self) -> None:
        resp = self.client.get(self.url, {'q': 'getting', 'type': 'page,comment'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['spaces'], [])
        self.assertGreaterEqual(len(resp.data['pages']), 1)

    def test_filter_by_space_key(self) -> None:
        resp = self.client.get(self.url, {'q': 'getting', 'space_key': 'ENG', 'type': 'page'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for page in resp.data['pages']:
            self.assertEqual(page['space_key'], 'ENG')

    def test_filter_status_draft(self) -> None:
        resp = self.client.get(self.url, {'q': 'architecture', 'type': 'page', 'status': 'draft'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['pages_count'], 1)
        self.assertTrue(resp.data['pages'][0]['is_draft'])

    def test_filter_status_published(self) -> None:
        resp = self.client.get(self.url, {'q': 'guide', 'type': 'page', 'status': 'published'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for page in resp.data['pages']:
            self.assertFalse(page['is_draft'])

    def test_filter_status_archived(self) -> None:
        resp = self.client.get(self.url, {'q': 'Legacy', 'type': 'page', 'status': 'archived'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['pages_count'], 1)

    def test_no_results(self) -> None:
        resp = self.client.get(self.url, {'q': 'xyznonexistent123'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_count'], 0)
        self.assertEqual(resp.data['pages'], [])
        self.assertEqual(resp.data['spaces'], [])
        self.assertEqual(resp.data['comments'], [])

    def test_pagination(self) -> None:
        resp = self.client.get(self.url, {'q': 'getting', 'page': '1', 'page_size': '1', 'type': 'page'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(resp.data['pages']), 1)
        self.assertEqual(resp.data['page'], 1)
        self.assertEqual(resp.data['page_size'], 1)

    def test_invalid_type_falls_back_to_all(self) -> None:
        resp = self.client.get(self.url, {'q': 'getting', 'type': 'invalid'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('pages', resp.data)
        self.assertIn('spaces', resp.data)
        self.assertIn('comments', resp.data)

    def test_page_size_capped_at_100(self) -> None:
        resp = self.client.get(self.url, {'q': 'getting', 'page_size': '999'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['page_size'], 100)

    def test_response_structure(self) -> None:
        resp = self.client.get(self.url, {'q': 'Getting Started', 'type': 'page'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        page_result = resp.data['pages'][0]
        self.assertIn('id', page_result)
        self.assertIn('result_type', page_result)
        self.assertIn('title', page_result)
        self.assertIn('space_name', page_result)
        self.assertIn('space_key', page_result)
        self.assertIn('created_by_username', page_result)

    def test_comment_response_includes_page_info(self) -> None:
        resp = self.client.get(self.url, {'q': 'helpful', 'type': 'comment'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        comment_result = resp.data['comments'][0]
        self.assertIn('page_title', comment_result)
        self.assertIn('space_key', comment_result)
        self.assertIn('author_username', comment_result)

    def test_case_insensitive_search(self) -> None:
        resp = self.client.get(self.url, {'q': 'GETTING STARTED', 'type': 'page'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(resp.data['pages_count'], 1)
