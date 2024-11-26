from urllib.parse import quote

from django.urls import reverse


def test_redirect_works(rasb_client):
    response = rasb_client.post(
        reverse("cookies_consent") + f"?redirect_back_to={quote('/test_page?test=yes')}",
        data={"do_you_want_to_accept_analytics_cookies": "True"},
    )
    assert rasb_client.session["redirect_back_to"] == "/test_page?test=yes"
    assert response.url == "/test_page?test=yes&cookies_set=true"

    # now will a URL without GET parameters
    response = rasb_client.post(
        reverse("cookies_consent") + f"?redirect_back_to={quote('/test_page')}",
        data={"do_you_want_to_accept_analytics_cookies": "True"},
    )
    assert rasb_client.session["redirect_back_to"] == "/test_page"
    assert response.url == "/test_page?cookies_set=true"

    # now with no redirect specified
    session = rasb_client.session
    session.pop("redirect_back_to", None)
    session.save()
    response = rasb_client.post(reverse("cookies_consent"), data={"do_you_want_to_accept_analytics_cookies": "True"})
    assert response.url == "/?cookies_set=true"
