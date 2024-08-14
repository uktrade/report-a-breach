from unittest.mock import patch

from django.http import HttpResponseRedirect
from django.urls import reverse
from report_a_suspected_breach.models import ReporterEmailVerification


class TestRequestVerifyCodeView:

    @patch("utils.notifier.send_email")
    def test_form_valid(self, patched_send_email, rasb_client):
        session = rasb_client.session
        session["reporter_email_address"] = "test@example.com"
        session.save()

        response = rasb_client.post(reverse("report_a_suspected_breach:request_verify_code"))

        email_verifications = ReporterEmailVerification.objects.all()
        assert len(email_verifications) == 1
        assert str(email_verifications[0].reporter_session) == rasb_client.session.session_key
        # Assert returns redirect

        redirect = HttpResponseRedirect(
            status=302, content_type="text/html; charset=utf-8", redirect_to=reverse("report_a_suspected_breach:verify_email")
        )
        assert response.status_code == redirect.status_code
        assert response["content-type"] == redirect["content-type"]
        assert response.url == redirect.url
        assert patched_send_email.called_once


@patch("django_ratelimit.decorators.is_ratelimited", return_value=True)
def test_ratelimit(mocked_is_ratelimited, rasb_client):
    session = rasb_client.session
    session.update({"reporter_email_address": "test@example.com"})
    session.save()

    response = rasb_client.post(reverse("report_a_suspected_breach:verify_email"), data={"email_verification_code": "123456"})
    assert response.status_code == 200
    assert "tried to verify your email too many times. Try again in 1 minute" in response.content.decode()
