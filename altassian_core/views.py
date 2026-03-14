import django
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Lightweight health probe for load balancers and uptime monitors."""
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = []

    def get(self, request: Request) -> Response:
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False

        return Response({
            'status': 'healthy' if db_ok else 'degraded',
            'version': django.get_version(),
            'database': 'connected' if db_ok else 'unavailable',
        })
