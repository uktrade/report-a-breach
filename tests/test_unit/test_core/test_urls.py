from django.test import override_settings
from django.urls import reverse

from tests.helpers import reload_urlconf


def test_private_urls_false(settings, rasb_client):
    settings.INCLUDE_PRIVATE_URLS = False
    reload_urlconf()
    assert not settings.INCLUDE_PRIVATE_URLS
    # assert can access rasb urls
    response = rasb_client.post(reverse("report_a_suspected_breach:start"), data={"reporter_professional_relationship": "owner"})

    assert response.status_code == 302
    assert response.url == reverse("report_a_suspected_breach:email")
    # assert vasb urls return 404 not found
    response = rasb_client.get("/view/")
    assert response.status_code == 404


@override_settings(INCLUDE_PRIVATE_URLS=True)
def test_private_urls_true(settings, rasb_client):
    reload_urlconf()
    assert settings.INCLUDE_PRIVATE_URLS
    # assert can access rasb urls
    response = rasb_client.post(reverse("report_a_suspected_breach:start"), data={"reporter_professional_relationship": "owner"})

    assert response.status_code == 302
    assert response.url == reverse("report_a_suspected_breach:email")
    # assert vasb urls return 403 forbidden
    response = rasb_client.get("/view/")
    assert response.status_code == 403
