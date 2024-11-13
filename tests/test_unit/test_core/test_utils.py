import datetime

from core.utils import update_last_activity_session_timestamp
from django.conf import settings
from django.utils import timezone


def test_update_last_activity_session_timestamp(request_object):
    session = request_object.session
    session.clear()
    session.save()
    assert not request_object.session.get(settings.SESSION_LAST_ACTIVITY_KEY)
    update_last_activity_session_timestamp(request_object)

    last_activity_timestamp = request_object.session.get(settings.SESSION_LAST_ACTIVITY_KEY)
    assert last_activity_timestamp
    last_activity_timestamp = datetime.datetime.fromisoformat(last_activity_timestamp)
    now = timezone.now()
    assert last_activity_timestamp < now
    # accounting for poor python speed on CircleCI, 2 seconds is ridiculous but should be enough
    assert (last_activity_timestamp - now).total_seconds() < 2
