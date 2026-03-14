from rest_framework.settings import api_settings
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Stricter rate limit for login attempts to mitigate brute-force attacks."""
    scope = 'login'
    THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES

    def get_rate(self) -> str | None:
        rates = getattr(api_settings, 'DEFAULT_THROTTLE_RATES', {}) or {}
        return rates.get(self.scope)

    def allow_request(self, request, view) -> bool:
        if not self.get_rate():
            return True
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)
