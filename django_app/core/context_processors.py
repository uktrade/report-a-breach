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
    return {
        "session_expiry_seconds": settings.SESSION_COOKIE_AGE,
        "session_expiry_minutes": settings.SESSION_COOKIE_AGE // 60,
        "session_expiry_hours": settings.SESSION_COOKIE_AGE // 60 // 60,
    }


def sentry_configuration_options(request: HttpRequest) -> dict[str, str | float]:
    """Add the Sentry configuration options to the context."""
    return {
        "SENTRY_ENABLED": settings.SENTRY_ENABLED,
        "SENTRY_DSN": settings.SENTRY_DSN,
        "SENTRY_ENVIRONMENT": settings.SENTRY_ENVIRONMENT,
        "SENTRY_ENABLE_TRACING": settings.SENTRY_ENABLE_TRACING,
        "SENTRY_TRACES_SAMPLE_RATE": settings.SENTRY_TRACES_SAMPLE_RATE,
    }


def environment_information(request: HttpRequest) -> dict[str, str]:
    """Add the current environment & branch to the context."""
    return {
        "CURRENT_ENVIRONMENT": settings.ENVIRONMENT,
        "CURRENT_BRANCH": settings.CURRENT_BRANCH,
        "CURRENT_TAG": settings.CURRENT_TAG,
        "CURRENT_COMMIT": settings.CURRENT_COMMIT,
    }
