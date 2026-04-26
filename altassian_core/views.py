"""Project-wide views — health check for GCP LB."""
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def get(self, request):
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return Response({"status": "ok"})
        except Exception as exc:  # noqa: BLE001
            return Response({"status": "degraded", "detail": str(exc)}, status=503)
