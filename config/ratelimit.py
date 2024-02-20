from django.conf import settings
from django.http import JsonResponse


def get_rate(group, request):
    """Return the rate limit for the given user. The Health Check user does not get rate-limited."""
    if not settings.API_RATELIMIT_ENABLED:
        return None

    return settings.API_RATELIMIT_RATE


def ratelimited_error(request, exception):
    """Return a 429 response when the user is rate-limited."""
    from sentry_sdk import capture_exception

    # logging to sentry so we know
    capture_exception(exception)
    return JsonResponse({"error": "ratelimited"}, status=429)
