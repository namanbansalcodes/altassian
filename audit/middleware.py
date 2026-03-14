from __future__ import annotations

import logging
from typing import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger('altassian.requests')

# HTTP methods that represent write operations
WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}


class RequestLoggingMiddleware:
    """Logs every request at INFO level for observability.

    Write operations (POST/PUT/PATCH/DELETE) that succeed are logged at INFO.
    All 5xx responses are logged at ERROR.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'anonymous'
        status_code = response.status_code
        method = request.method
        path = request.get_full_path()

        log_line = f"{method} {path} {status_code} user={username}"

        if status_code >= 500:
            logger.error(log_line)
        elif method in WRITE_METHODS and 200 <= status_code < 300:
            logger.info(log_line)
        else:
            logger.debug(log_line)

        return response
