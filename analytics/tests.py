from django.test import TestCase
from rest_framework.test import APIClient

from analytics.models import PageView
from pages.models import Comment, Page, PageVersion
from spaces.models import Space
from user_accounts.models import CustomUser


class AnalyticsTestBase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='analyst', password='testpass123', email='analyst@test.com',
            role='admin',
        )
        self.client.force_authenticate(user=self.user)

        self.space = Space.objects.create(
            name='Test Space', key='TEST', owner=self.user,
        )
        self.page = Page.objects.create(
            title='Test Page', space=self.space, body_markdown='# Hello',
            body_html='<h1>Hello</h1>', created_by=self.user,
            updated_by=self.user, position=0,
        )


class PageViewModelTests(AnalyticsTestBase):
    def test_create_page_view(self) -> None:
        pv = PageView.objects.create(page=self.page, user=self.user)
        self.assertEqual(pv.page, self.page)
        self.assertEqual(pv.user, self.user)
        self.assertIsNotNone(pv.viewed_at)

    def test_anonymous_page_view(self) -> None:
        pv = PageView.objects.create(page=self.page, user=None)
        self.assertIsNone(pv.user)


class TrackViewTests(AnalyticsTestBase):
    def test_track_page_view(self) -> None:
        resp = self.client.post('/api/analytics/track-view/', {
            'page': self.page.id,
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(PageView.objects.count(), 1)

    def test_track_view_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        resp = self.client.post('/api/analytics/track-view/', {
            'page': self.page.id,
        })
        self.assertEqual(resp.status_code, 401)


class OverviewTests(AnalyticsTestBase):
    def test_overview_returns_counts(self) -> None:
        PageView.objects.create(page=self.page, user=self.user)
        Comment.objects.create(page=self.page, author=self.user, body='Nice')

        resp = self.client.get('/api/analytics/overview/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_users'], 1)
        self.assertEqual(data['total_spaces'], 1)
        self.assertEqual(data['total_pages'], 1)
        self.assertEqual(data['total_comments'], 1)
        self.assertEqual(data['total_page_views'], 1)
        self.assertIn('new_users_last_7d', data)
        self.assertIn('views_last_7d', data)

    def test_overview_unauthenticated(self) -> None:
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/analytics/overview/')
        self.assertEqual(resp.status_code, 401)


class UserActivityTests(AnalyticsTestBase):
    def test_user_activity(self) -> None:
        PageView.objects.create(page=self.page, user=self.user)
        Comment.objects.create(page=self.page, author=self.user, body='Test')

        resp = self.client.get('/api/analytics/user-activity/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data) >= 1)
        entry = data[0]
        self.assertEqual(entry['username'], 'analyst')
        self.assertGreaterEqual(entry['pages_created'], 1)

    def test_user_activity_with_days_param(self) -> None:
        resp = self.client.get('/api/analytics/user-activity/?days=7')
        self.assertEqual(resp.status_code, 200)


class ContentActivityTests(AnalyticsTestBase):
    def test_content_activity(self) -> None:
        PageView.objects.create(page=self.page, user=self.user)

        resp = self.client.get('/api/analytics/content-activity/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]['title'], 'Test Page')
        self.assertEqual(data[0]['space_key'], 'TEST')

    def test_content_activity_filter_by_space(self) -> None:
        resp = self.client.get('/api/analytics/content-activity/?space_key=TEST')
        self.assertEqual(resp.status_code, 200)


class ActivityTimelineTests(AnalyticsTestBase):
    def test_timeline_default_30_days(self) -> None:
        resp = self.client.get('/api/analytics/activity-timeline/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 30)
        for point in data:
            self.assertIn('date', point)
            self.assertIn('views', point)
            self.assertIn('edits', point)
            self.assertIn('comments', point)
            self.assertIn('new_pages', point)

    def test_timeline_custom_days(self) -> None:
        resp = self.client.get('/api/analytics/activity-timeline/?days=7')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 7)
