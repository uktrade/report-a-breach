from unittest.mock import MagicMock, patch

from core.sites import SiteName
from django.contrib.auth.models import User
from django.test import RequestFactory
from view_a_suspected_breach.views import AdminViewABreachView, ViewABreachView


class TestViewASuspectedBreach:

    @patch("view_a_suspected_breach.views.send_email")
    def test_successful_view_a_suspected_breach(self, mock_email, vasb_client):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=False,
        )

        request_object = RequestFactory().get("/")

        request_object.user = test_user
        view = ViewABreachView()
        view.setup(request_object)
        response = view.get(
            request_object,
            headers={"x-requested-with": "XMLHttpRequest"},
        )

        assert response.status_code == 200
        mock_email.assert_not_called()

    @patch("view_a_suspected_breach.views.send_email")
    def test_get_unauthorised_view(self, mock_email, vasb_client):
        mock_email.send_email = MagicMock()
        test_user = User.objects.create_user(
            "Jane",
            "test@example.com",
        )

        User.objects.create_user(
            "Polly",
            "polly@example.com",
            is_staff=True,
        )

        request_object = RequestFactory().get("/")
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach
        request_object.user = test_user
        view = ViewABreachView()
        view.setup(request_object)
        response = view.get(
            request_object,
            headers={"x-requested-with": "XMLHttpRequest"},
        )

        assert response.status_code == 200
        mock_email.assert_called_once()


class TestAdminViewABreach:

    def test_admin_view_a_breach_unauthorised(self, vasb_client):
        test_user = User.objects.create_user(
            "Jane",
            "test@example.com",
        )

        request_object = RequestFactory().get("/")
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach
        request_object.user = test_user
        view = AdminViewABreachView()
        view.setup(request_object)
        response = view.get(
            request_object,
            headers={"x-requested-with": "XMLHttpRequest"},
        )

        assert response.status_code == 401

    def test_successful_admin_view_a_breach(self, vasb_client):
        test_user = User.objects.create_user(
            "Joan",
            "joan@example.com",
            is_staff=True,
        )

        request_object = RequestFactory().get("/")
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach
        request_object.user = test_user
        view = AdminViewABreachView()
        view.setup(request_object)
        response = view.get(
            request_object,
            headers={"x-requested-with": "XMLHttpRequest"},
        )

        assert response.status_code == 200
