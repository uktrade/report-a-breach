from unittest.mock import MagicMock, patch

from core.sites import SiteName
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory
from django.urls import reverse
from view_a_suspected_breach.views import ManageUsersView, ViewASuspectedBreachView


class TestViewASuspectedBreach:
    @patch("view_a_suspected_breach.mixins.send_email")
    def test_successful_view_a_suspected_breach(self, mock_email, vasb_client, breach_object):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )

        request_object = RequestFactory().get(reverse("view_a_suspected_breach:breach_report", args=[breach_object.id]))
        request_object.user = test_user
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach

        vasb_client.force_login(test_user)

        view = ViewASuspectedBreachView()
        view.setup(request_object, pk=breach_object.id)
        response = view.dispatch(request_object)

        assert response.status_code == 200
        mock_email.assert_not_called()

    @patch("view_a_suspected_breach.mixins.send_email")
    def test_get_unauthorised_view(self, mock_email, vasb_client, breach_object):
        mock_email.send_email = MagicMock()
        test_user = User.objects.create_user(
            "Jane",
            "test@example.com",
            is_active=False,
        )

        User.objects.create_user(
            "Polly",
            "polly@example.com",
            is_staff=True,
        )

        request_object = RequestFactory().get(reverse("view_a_suspected_breach:breach_report", args=[breach_object.id]))
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach
        request_object.user = test_user
        view = ViewASuspectedBreachView()
        view.setup(request_object, pk=breach_object.id)
        vasb_client.force_login(test_user)
        response = view.dispatch(request_object)

        assert response.status_code == 200
        mock_email.assert_called_once()

    def test_anonymous_user(self, vasb_client, breach_object):
        request_object = RequestFactory().get(reverse("view_a_suspected_breach:breach_report", args=[breach_object.id]))
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach
        request_object.user = AnonymousUser()
        view = ViewASuspectedBreachView()
        view.setup(request_object, pk=breach_object.id)
        response = view.dispatch(request_object)

        # we should be redirected to the login page
        assert response.status_code == 302
        assert "login" in response.url


class TestAdminManageUsers:
    def test_admin_view_a_breach_unauthorised(self, vasb_client):
        test_user = User.objects.create_user(
            "Jane",
            "test@example.com",
            is_staff=False,
        )

        request_object = RequestFactory().get("/")
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach
        request_object.user = test_user
        view = ManageUsersView()
        view.setup(request_object)
        response = view.dispatch(request_object)

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
        view = ManageUsersView()
        view.setup(request_object)
        response = view.dispatch(request_object)

        assert response.status_code == 200

    def test_base_redirect_view_staff(self, vasb_client):
        """Logged-in users who are staff should be redirected to the view-all-reports page"""
        staff_user = User.objects.create_user("Joan", "joan@example.com", is_active=True, is_staff=True)
        vasb_client.force_login(staff_user)
        response = vasb_client.get("/")
        assert response.status_code == 302

    def test_base_redirect_view_not_staff(self, vasb_client):
        """Logged-in users who are not staff should be redirected to the view-all-reports page"""
        staff_user = User.objects.create_user("Joan", "joan@example.com", is_active=True, is_staff=False)
        vasb_client.force_login(staff_user)
        response = vasb_client.get("/")
        assert response.status_code == 302


def test_all_views_require_login():
    # gets all views from view_a_suspected_breach and asserts that they all require login
    from view_a_suspected_breach.urls import urlpatterns

    views = []
    for pattern in urlpatterns:
        if hasattr(pattern.callback, "cls"):
            view = pattern.callback.cls
        elif hasattr(pattern.callback, "view_class"):
            view = pattern.callback.view_class
        else:
            view = pattern.callback
        views.append(view)

    for view in views:
        assert issubclass(view, LoginRequiredMixin)
