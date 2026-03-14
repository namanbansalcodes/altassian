from django.contrib.sitemaps import Sitemap

from pages.models import Page
from spaces.models import Space


class PageSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Page.objects.filter(is_draft=False, noindex=False).select_related('space').order_by('-updated_at')

    def lastmod(self, obj: Page):
        return obj.updated_at

    def location(self, obj: Page) -> str:
        return f'/spaces/{obj.space.key}/pages/{obj.slug}'


class SpaceSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6
    protocol = 'https'

    def items(self):
        return Space.objects.filter(is_archived=False).order_by('-created_at')

    def lastmod(self, obj: Space):
        return obj.created_at

    def location(self, obj: Space) -> str:
        return f'/spaces/{obj.key}'


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 1.0
    protocol = 'https'

    def items(self):
        return ['/', '/login', '/register', '/spaces']

    def location(self, item: str) -> str:
        return item
