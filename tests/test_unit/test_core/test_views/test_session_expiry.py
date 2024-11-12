import datetime
from time import sleep

from django.conf import settings
from django.urls import reverse
from django.utils import timezone


def test_session_not_expired(rasb_client):
    session = rasb_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = now_time.isoformat()
    session.save()
    sleep(1)

    response = rasb_client.post(
        reverse("report_a_suspected_breach:email"), follow=True, data={"reporter_email_address": "test@example.com"}
    )
    new_updated_activity_time = datetime.datetime.fromisoformat(rasb_client.session[settings.SESSION_LAST_ACTIVITY_KEY])

    assert new_updated_activity_time > now_time
    assert response.status_code == 200

    # we want to make sure we're actually being progressed to the next step
    assert response.resolver_match.url_name == "verify_email"


def test_session_expired(rasb_client):
    session = rasb_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = (now_time + datetime.timedelta(hours=-30)).isoformat()
    session.save()
    sleep(1)

    response = rasb_client.post(reverse("report_a_suspected_breach:email"), follow=True)

    # we want to make sure we're actually being progressed to the session expired page
    assert response.resolver_match.url_name == "session_expired"
    assert dict(rasb_client.session) == {}


def test_no_session_key(rasb_client):
    assert dict(rasb_client.session) == {}
    response = rasb_client.post(
        reverse("report_a_suspected_breach:email"), follow=True, data={"reporter_email_address": "test@example.com"}
    )
    assert response.resolver_match.url_name == "session_expired"
    assert dict(rasb_client.session) == {}


def test_ping_session_view(rasb_client):
    response = rasb_client.get(reverse("ping_session"))
    assert response.status_code == 200
    assert response.content == b"pong"
    assert rasb_client.session[settings.SESSION_LAST_ACTIVITY_KEY]


def test_expired_session_view(rasb_client):
    session = rasb_client.session

    now_time = timezone.now()
    session[settings.SESSION_LAST_ACTIVITY_KEY] = (now_time + datetime.timedelta(hours=-30)).isoformat()
    session.save()

    response = rasb_client.get(reverse("session_expired"))
    assert response.status_code == 200
    assert not dict(rasb_client.session)
