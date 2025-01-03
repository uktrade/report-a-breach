from unittest.mock import MagicMock, patch

from core.sites import SiteName
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse


class TestPrivateURLs:
    @patch("view_a_suspected_breach.mixins.send_email")
    def test_private_urls_false(self, mock_email, settings, rasb_client, vasb_client, breach_object):
        settings.INCLUDE_PRIVATE_URLS = False
        assert not settings.INCLUDE_PRIVATE_URLS
        print(settings.INCLUDE_PRIVATE_URLS)
        # assert can access rasb urls
        response = rasb_client.post(
            reverse("report_a_suspected_breach:start"), data={"reporter_professional_relationship": "owner"}
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:email")
        # assert can not access vasb urls
        test_user = User.objects.create_user(
            "John",
            "test1@example.com",
            is_active=True,
        )

        request = RequestFactory().get("/")
        request.user = test_user
        request.site = SiteName
        request.site.name = SiteName.view_a_suspected_breach

        vasb_client.force_login(test_user)
        request.session = MagicMock()

        assert vasb_client.get("/")
        assert response.status_code == 404
        assert mock_email.call_count == 0
