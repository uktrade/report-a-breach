# from unittest.mock import patch

from django.http import HttpResponseRedirect
from django.test import RequestFactory

# from django.urls import reverse
from report_a_suspected_breach.forms import SummaryForm
from report_a_suspected_breach.models import ReporterEmailVerification
from report_a_suspected_breach.views.views_a import EmailVerifyView


class TestRequestVerifyCodeView:
    def test_form_valid(self, rasb_client):
        reporter_email_address = "test@testmail.com"
        view = EmailVerifyView()

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

        # Assert returns redirect
        redirect = HttpResponseRedirect(
            status=302, content_type="text/html; charset=utf-8", redirect_to="/report_a_suspected_breach/verify_email"
        )

        assert response.status_code == redirect.status_code
        assert response["content-type"] == redirect["content-type"]
        assert response.url == redirect.url

    # TODO: to be updated as part of ticket DST-508
    # @patch("django_ratelimit.decorators.is_ratelimited", return_value=True)
    # def test_ratelimit(self, mocked_is_ratelimited, rasb_client):
    #     session = rasb_client.session
    #     session.update({"reporter_email_address": "test@example.com"})
    #     session.save()
    #
    #     response = rasb_client.post(reverse("report_a_suspected_breach:verify_email"))
    #     assert response.status_code == 200
    #     assert "You've tried to request a new code too many times. Please try again in 1 minute" in response.content.decode()
