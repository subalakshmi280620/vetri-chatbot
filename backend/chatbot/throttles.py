from rest_framework.exceptions import APIException
from rest_framework.throttling import AnonRateThrottle


class ChatRateLimitExceeded(APIException):
    status_code = 429
    default_code = "rate_limit_exceeded"

    def __init__(self, wait=None):
        detail = {
            "error": "Too many chat requests. Please wait a minute and try again.",
        }
        if wait is not None:
            detail["retry_after_seconds"] = int(wait)
        super().__init__(detail=detail)


class ChatRateThrottle(AnonRateThrottle):
    """Limit chat POST requests per client IP address."""

    scope = "chat"

    def throttle_failure(self):
        raise ChatRateLimitExceeded(wait=self.wait())
