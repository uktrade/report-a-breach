from django.test import override_settings
from django.urls import reverse
from view_a_suspected_breach.utils import (
    craft_view_a_suspected_breach_url,
    get_view_a_suspected_breach_url,
)


@override_settings(PROTOCOL="https://", VIEW_A_SUSPECTED_BREACH_DOMAIN="view-a-suspected-breach.com")
def test_craft_view_a_suspected_breach_url():
    url = craft_view_a_suspected_breach_url("/view-report/123/")
    assert url == "https://view-a-suspected-breach.com/view-report/123/"


@override_settings(PROTOCOL="https://", VIEW_A_SUSPECTED_BREACH_DOMAIN="view-a-suspected-breach.com")
def test_get_view_a_suspected_breach_application_url():
    url = get_view_a_suspected_breach_url("123")
    assert url == "https://view-a-suspected-breach.com/view/view-report/123/"


@override_settings(PROTOCOL="", VIEW_A_SUSPECTED_BREACH_DOMAIN="")
def test_get_view_a_suspected_breach_application_url_matches_hardcoded_url():
    # checks that the hardcoded URL matches the expected URL
    actual_url = reverse("view_a_suspected_breach:breach_report", kwargs={"reference": "123"})
    crafted_url = get_view_a_suspected_breach_url("123")
    assert crafted_url == actual_url
