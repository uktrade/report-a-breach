from django.http import HttpResponse
from django.test import RequestFactory
from report_a_suspected_breach.models import ReporterEmailVerification, Session
from report_a_suspected_breach.views import EmailVerifyView


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
