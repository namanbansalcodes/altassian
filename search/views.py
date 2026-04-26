from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchRank
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pages.models import Page


class SearchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        space_slug = request.query_params.get("space")
        if not q:
            return Response({"results": []})

        query = SearchQuery(q, config="english")
        qs = Page.objects.filter(deleted_at__isnull=True, search_vector=query)
        if space_slug:
            qs = qs.filter(space__slug=space_slug)
        qs = (
            qs.annotate(rank=SearchRank(F("search_vector"), query))
            .annotate(
                snippet_html=SearchHeadline(
                    "body_md", query, config="english",
                    start_sel="<b>", stop_sel="</b>", max_words=30, min_words=15,
                )
            )
            .select_related("space")
            .order_by("-rank")[:20]
        )

        results = [
            {
                "page_id": p.id,
                "space_slug": p.space.slug,
                "page_slug": p.slug,
                "title": p.title,
                "snippet_html": p.snippet_html,
                "rank": float(p.rank),
            }
            for p in qs
        ]
        return Response({"results": results})
