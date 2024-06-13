from unittest.mock import patch

from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from report_a_suspected_breach.forms import SummaryForm
from report_a_suspected_breach.models import ReporterEmailVerification
from report_a_suspected_breach.views import RequestVerifyCodeView


class TestRequestVerifyCodeView:
    @patch("utils.notifier.send_email")
    def test_form_valid(self, send_email_mock, rasb_client):
        reporter_email_address = "test@testmail.com"
        view = RequestVerifyCodeView()

        # Setup Session values
        request_object = RequestFactory().get("/")
        request_object.session = rasb_client.session
        request_object.session["reporter_email_address"] = reporter_email_address
        request_object.session.save()

        # Setup View
        view.setup(request_object)

        # Call form_valid method of view
        response = view.form_valid(SummaryForm)

        # Assert ReporterEmailVerification object created
        email_verifications = ReporterEmailVerification.objects.all()
        assert len(email_verifications) == 1
        assert str(email_verifications[0].reporter_session) == request_object.session.session_key

        assert send_email_mock.call_count == 1

        # Assert returns redirect
        redirect = HttpResponseRedirect(
            status=302, content_type="text/html; charset=utf-8", redirect_to="/report_a_suspected_breach/email_verify"
        )

        assert response.status_code == redirect.status_code
        assert response["content-type"] == redirect["content-type"]
        assert response.url == redirect.url

    @patch("django_ratelimit.decorators.is_ratelimited", return_value=True)
    def test_ratelimit(self, mocked_is_ratelimited, rasb_client):
        session = rasb_client.session
        session.update({"reporter_email_address": "test@example.com"})
        session.save()

        response = rasb_client.post(reverse("report_a_suspected_breach:request_verify_code"))
        assert response.status_code == 200
        assert "You've tried to request a new code too many times. Please try again in 1 minute" in response.content.decode()
