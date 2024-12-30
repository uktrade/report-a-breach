from datetime import timedelta
from unittest.mock import patch

from django.http import HttpResponse, HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from report_a_suspected_breach.models import ReporterEmailVerification, Session
from report_a_suspected_breach.views.views_start import (
    EmailVerifyView,
    WhatIsYourEmailAddressView,
)


class TestStartView:
    def test_redirect_after_post(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:start") + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
            data={"reporter_professional_relationship": "owner"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:check_your_answers")

        # now changing the answer and checking that redirect to returns False
        response = rasb_client.post(
            reverse("report_a_suspected_breach:start") + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
            data={"reporter_professional_relationship": "third_party"},
        )
        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:email")

    def test_success_url(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:start"), data={"reporter_professional_relationship": "owner"}
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:email")

        # now checking for when the user has already provided their email
        session = rasb_client.session
        session["reporter_email_address"] = "test@example.com"
        session.save()

        response = rasb_client.post(
            reverse("report_a_suspected_breach:start"), data={"reporter_professional_relationship": "owner"}
        )
        assert response.url == reverse("report_a_suspected_breach:name")


class TestWhatIsYourEmailAddressView:
    def test_post(self, rasb_client):
        request_object = RequestFactory().get("/")
        request_object.session = rasb_client.session
        view = WhatIsYourEmailAddressView()
        view.setup(request_object)
        data = {"reporter_email_address": "test@123.com"}
        response = rasb_client.post(
            reverse("report_a_suspected_breach:email"),
            data=data,
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:verify_email")


class TestEmailVerifyCodeView:
    def test_post(self, rasb_client):
        request_object = RequestFactory().get("/")

        request_object.session = rasb_client.session
        session = rasb_client.session
        reporter_email_address = "test@testmail.com"
        session["reporter_email_address"] = reporter_email_address
        session.save()
        view = EmailVerifyView()
        view.setup(request_object)
        verify_code = "012345"
        user_session = Session.objects.get(session_key=session.session_key)
        ReporterEmailVerification.objects.create(
            reporter_session=user_session,
            email_verification_code=verify_code,
        )
        data = {"email_verification_code": verify_code}
        response = view.post(request_object, data)

        # Assert returns success redirect
        expected_response = HttpResponse(status=200, content_type="text/html; charset=utf-8")

        assert response.status_code == expected_response.status_code
        assert response["content-type"] == expected_response["content-type"]

    @patch("django_ratelimit.decorators.is_ratelimited", return_value=True)
    def test_ratelimit(self, mocked_is_ratelimited, rasb_client):
        ReporterEmailVerification.objects.create(
            reporter_session=rasb_client.session._get_session_from_db(), email_verification_code="123456"
        )

        # rate limit response
        response = rasb_client.post(reverse("report_a_suspected_breach:verify_email"), data={"email_verification_code": "123456"})
        assert response.status_code == 200
        assert response.wsgi_request.limited is True
        form = response.context["form"]
        assert "email_verification_code" in form.errors
        assert (
            form.errors.as_data()["email_verification_code"][0].message
            == "You've tried to verify your email too many times. Try again in 1 minute"
        )

    @patch("report_a_suspected_breach.views.views_start.verify_email")
    def test_form_invalid_resent_code(self, mocked_verify_email, rasb_client):
        session = rasb_client.session
        session["reporter_email_address"] = "test@example.com"
        session.save()

        verification = ReporterEmailVerification.objects.create(
            reporter_session=rasb_client.session._get_session_from_db(), email_verification_code="123456"
        )
        verification.date_created = verification.date_created - timedelta(minutes=30)
        verification.save()

        response = rasb_client.post(reverse("report_a_suspected_breach:verify_email"), data={"email_verification_code": "123456"})
        assert response.status_code == 200
        assert mocked_verify_email.called_once
        assert mocked_verify_email.called_with("test@example.com")


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
