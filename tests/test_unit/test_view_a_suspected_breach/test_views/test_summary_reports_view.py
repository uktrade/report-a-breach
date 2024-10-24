from unittest.mock import MagicMock, patch

from core.sites import SiteName
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse


class TestSummaryReportsView:

    @patch("view_a_suspected_breach.mixins.send_email")
    def test_summary_reports_view(self, mock_email, vasb_client, breach_object):
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

        response = vasb_client.get(reverse("view_a_suspected_breach:summary_reports"))
        assert response.status_code == 200
        assert mock_email.call_count == 0
