import json
import logging
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from pages.models import Page, PageVersion, Comment
from spaces.models import Space
from user_accounts.permissions import IsEditorOrAbove

logger = logging.getLogger('altassian')


class ExportSpaceView(APIView):
    """Export an entire space (pages + comments) as JSON."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, space_key: str) -> HttpResponse:
        try:
            space = Space.objects.get(key=space_key)
        except Space.DoesNotExist:
            return Response({'detail': 'Space not found.'}, status=status.HTTP_404_NOT_FOUND)

        pages = Page.objects.filter(space=space).order_by('position', 'created_at')
        export_data = {
            'format_version': '1.0',
            'exported_at': timezone.now().isoformat(),
            'exported_by': request.user.username,
            'space': {
                'name': space.name,
                'key': space.key,
                'description': space.description or '',
            },
            'pages': [],
        }

        for page in pages:
            comments = Comment.objects.filter(page=page).order_by('created_at')
            versions = PageVersion.objects.filter(page=page).order_by('version_number')
            page_data = {
                'title': page.title,
                'slug': page.slug,
                'body_markdown': page.body_markdown,
                'body_html': page.body_html,
                'position': page.position,
                'is_draft': page.is_draft,
                'parent_slug': page.parent.slug if page.parent else None,
                'created_at': page.created_at.isoformat(),
                'versions': [
                    {
                        'version_number': v.version_number,
                        'body_markdown': v.body_markdown,
                        'change_summary': v.change_summary or '',
                        'created_at': v.created_at.isoformat(),
                    }
                    for v in versions
                ],
                'comments': [
                    {
                        'body': c.body,
                        'author_username': c.author.username,
                        'created_at': c.created_at.isoformat(),
                    }
                    for c in comments if c.parent is None
                ],
            }
            export_data['pages'].append(page_data)

        content = json.dumps(export_data, indent=2, default=str)
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="space_{space_key}_export.json"'
        logger.info('Space %s exported by user %s', space_key, request.user.username)
        return response


class ImportSpaceView(APIView):
    """Import a space from a JSON export file."""

    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser]

    def post(self, request: Request) -> Response:
        data = request.data

        if hasattr(data, 'read'):
            data = json.loads(data.read())
        elif isinstance(data, str):
            data = json.loads(data)

        if 'file' in request.FILES:
            data = json.loads(request.FILES['file'].read())

        if not isinstance(data, dict) or 'space' not in data or 'pages' not in data:
            return Response(
                {'detail': 'Invalid import format. Expected {space, pages}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        space_data = data['space']
        space_key = space_data.get('key', '')

        if Space.objects.filter(key=space_key).exists():
            return Response(
                {'detail': f'Space with key "{space_key}" already exists.'},
                status=status.HTTP_409_CONFLICT,
            )

        space = Space.objects.create(
            name=space_data['name'],
            key=space_key,
            description=space_data.get('description', ''),
            owner=request.user,
        )

        slug_to_page = {}
        pages_data = data.get('pages', [])

        # First pass: create pages without parent references
        for page_data in pages_data:
            page = Page.objects.create(
                title=page_data['title'],
                slug=page_data.get('slug'),
                space=space,
                body_markdown=page_data.get('body_markdown', ''),
                body_html=page_data.get('body_html', ''),
                position=page_data.get('position', 0),
                is_draft=page_data.get('is_draft', False),
                created_by=request.user,
                updated_by=request.user,
            )
            slug_to_page[page.slug] = page

            for v_data in page_data.get('versions', []):
                PageVersion.objects.create(
                    page=page,
                    version_number=v_data['version_number'],
                    body_markdown=v_data['body_markdown'],
                    change_summary=v_data.get('change_summary', ''),
                    edited_by=request.user,
                )

        # Second pass: set parent references
        for page_data in pages_data:
            parent_slug = page_data.get('parent_slug')
            if parent_slug and parent_slug in slug_to_page:
                page = slug_to_page.get(page_data.get('slug'))
                if page:
                    page.parent = slug_to_page[parent_slug]
                    page.save(update_fields=['parent'])

        logger.info(
            'Space %s imported by user %s (%d pages)',
            space_key, request.user.username, len(pages_data),
        )

        return Response(
            {
                'detail': f'Space "{space.name}" imported successfully.',
                'space_key': space.key,
                'pages_imported': len(pages_data),
            },
            status=status.HTTP_201_CREATED,
        )


class BulkPagesView(APIView):
    """Bulk operations on pages within a space."""

    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request: Request) -> Response:
        """Bulk create pages in a space."""
        space_key = request.data.get('space_key')
        pages_data = request.data.get('pages', [])

        if not space_key:
            return Response({'detail': 'space_key is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not pages_data:
            return Response({'detail': 'pages list is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            space = Space.objects.get(key=space_key)
        except Space.DoesNotExist:
            return Response({'detail': 'Space not found.'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        errors = []
        for idx, page_data in enumerate(pages_data):
            title = page_data.get('title', '').strip()
            if not title:
                errors.append({'index': idx, 'error': 'Title is required.'})
                continue
            try:
                page = Page.objects.create(
                    title=title,
                    space=space,
                    body_markdown=page_data.get('body_markdown', ''),
                    body_html=page_data.get('body_html', ''),
                    position=page_data.get('position', 0),
                    is_draft=page_data.get('is_draft', False),
                    created_by=request.user,
                    updated_by=request.user,
                )
                created.append({'id': page.id, 'title': page.title, 'slug': page.slug})
            except Exception as exc:
                errors.append({'index': idx, 'error': str(exc)})

        return Response({
            'created_count': len(created),
            'error_count': len(errors),
            'created': created,
            'errors': errors,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)

    def patch(self, request: Request) -> Response:
        """Bulk update page status (publish/draft/archive)."""
        page_ids = request.data.get('page_ids', [])
        action = request.data.get('action')

        if not page_ids:
            return Response({'detail': 'page_ids list is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if action not in ('publish', 'draft'):
            return Response(
                {'detail': 'action must be "publish" or "draft".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_draft = action == 'draft'
        updated = Page.objects.filter(id__in=page_ids).update(is_draft=is_draft)

        return Response({
            'detail': f'{updated} pages updated to {action}.',
            'updated_count': updated,
        })

    def delete(self, request: Request) -> Response:
        """Bulk delete pages by IDs."""
        page_ids = request.data.get('page_ids', [])
        if not page_ids:
            return Response({'detail': 'page_ids list is required.'}, status=status.HTTP_400_BAD_REQUEST)

        pages = Page.objects.filter(id__in=page_ids)
        count = pages.count()
        pages.delete()

        return Response({'detail': f'{count} pages deleted.', 'deleted_count': count})
