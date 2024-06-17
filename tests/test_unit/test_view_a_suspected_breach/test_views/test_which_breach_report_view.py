from unittest.mock import patch

from core.sites import SiteName
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.urls import reverse
from view_a_suspected_breach.views import WhichBreachReportView


class TestWhichBreachReportView:

    @patch("view_a_suspected_breach.mixins.send_email")
    def test_successful_view_a_suspected_breach(self, mock_email, vasb_client, breacher_and_supplier_object):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )

        request_object = RequestFactory().get(reverse("view_a_suspected_breach:landing"))
        request_object.user = test_user
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach

        vasb_client.force_login(test_user)

        view = WhichBreachReportView()
        view.setup(request_object, pk=breacher_and_supplier_object.reference)
        response = view.get(request_object)

        assert response.status_code == 200
        mock_email.assert_not_called()
