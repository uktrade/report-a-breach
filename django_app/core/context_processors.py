from django.conf import settings
from django.http import HttpRequest


def truncate_words_limit(request: HttpRequest) -> dict[str, int]:
    return {
        "truncate_words_limit": settings.TRUNCATE_WORDS_LIMIT,
    }


def back_button(request: HttpRequest) -> dict[str, str]:
    """Default back button values - can be overridden in the context dictionary of a view."""
    return {"back_button_text": "Back", "back_button_link": request.META.get("HTTP_REFERER", None)}


def is_debug_mode(request: HttpRequest) -> dict[str, bool]:
    """Add a flag to the context to indicate if the site is in debug mode."""
    return {"is_debug_mode": settings.DEBUG}


def session_expiry_times(request: HttpRequest) -> dict[str, int]:
    """Add the session expiry time in seconds & minutes to the context."""
    return {"session_expiry_seconds": settings.SESSION_COOKIE_AGE, "session_expiry_minutes": settings.SESSION_COOKIE_AGE / 60}
