from unittest.mock import patch

from django.http import HttpResponseRedirect
from django.test import RequestFactory
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