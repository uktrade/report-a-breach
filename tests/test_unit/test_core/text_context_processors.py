from core.context_processors import (
    environment_information,
    sentry_configuration_options,
    session_expiry_times,
)
from django.test import override_settings


@override_settings(SESSION_COOKIE_AGE=10800)
def test_session_expiry_times(request_object):
    assert session_expiry_times(request_object) == {
        "session_expiry_seconds": 10800,
        "session_expiry_minutes": 180,
        "session_expiry_hours": 3,
    }


@override_settings(
    SENTRY_ENABLED=False,
    SENTRY_DSN="https://example.com",
    SENTRY_ENVIRONMENT="test",
    SENTRY_ENABLE_TRACING=False,
    SENTRY_TRACES_SAMPLE_RATE=0.0,
)
def test_sentry_configuration_options(request_object):
    assert sentry_configuration_options(request_object) == {
        "SENTRY_ENABLED": False,
        "SENTRY_DSN": "https://example.com",
        "SENTRY_ENVIRONMENT": "test",
        "SENTRY_ENABLE_TRACING": False,
        "SENTRY_TRACES_SAMPLE_RATE": 0.0,
    }


@override_settings(
    ENVIRONMENT="test",
    CURRENT_BRANCH="test-branch",
    CURRENT_TAG="v1.0.0",
)
def test_environment_information(request_object):
    assert environment_information(request_object) == {
        "current_environment": "test",
        "current_branch": "test-branch",
        "current_tag": "v1.0.0",
    }
