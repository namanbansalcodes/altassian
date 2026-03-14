import math
from typing import Any, Dict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Page-number pagination with client-configurable page size and total_pages metadata."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: list) -> Response:
        total_pages = math.ceil(self.page.paginator.count / self.get_page_size(self.request))
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": total_pages,
                "current_page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["count", "total_pages", "current_page", "page_size", "results"],
            "properties": {
                "count": {"type": "integer", "example": 123},
                "total_pages": {"type": "integer", "example": 7},
                "current_page": {"type": "integer", "example": 1},
                "page_size": {"type": "integer", "example": 20},
                "next": {"type": "string", "nullable": True, "format": "uri"},
                "previous": {"type": "string", "nullable": True, "format": "uri"},
                "results": schema,
            },
        }
