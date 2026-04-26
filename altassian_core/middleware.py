"""Project-level middleware."""
from django.http import JsonResponse


class HealthCheckBypassMiddleware:
    """
    Serve `/api/health` for any Host header so GCP LB health checks don't trip
    Django's ALLOWED_HOSTS guard. The check itself only verifies the DB is up.
    """

    HEALTH_PATH = "/api/health"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == self.HEALTH_PATH:
            from django.db import connection
            try:
                with connection.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
                return JsonResponse({"status": "ok"})
            except Exception as exc:  # noqa: BLE001
                return JsonResponse(
                    {"status": "degraded", "detail": str(exc)},
                    status=503,
                )
        return self.get_response(request)
