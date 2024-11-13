from core.context_processors import session_expiry_times
from django.test import override_settings


@override_settings(SESSION_COOKIE_AGE=10800)
def test_session_expiry_times(request_object):
    assert session_expiry_times(request_object) == {
        "session_expiry_seconds": 10800,
        "session_expiry_minutes": 180,
        "session_expiry_hours": 3,
    }
