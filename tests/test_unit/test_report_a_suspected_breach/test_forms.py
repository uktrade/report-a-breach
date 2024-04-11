from datetime import timedelta

import pytest
from django.test import RequestFactory
from report_a_suspected_breach.forms import EmailVerifyForm
from report_a_suspected_breach.models import ReporterEmailVerification


class TestEmailVerifyForm:
    verify_code = "123456"

    @pytest.fixture(autouse=True)
    def reporter_email_verification_object(self, rasb_client):
        self.obj = ReporterEmailVerification.objects.create(
            reporter_session=rasb_client.session._get_session_from_db(),
            email_verification_code=self.verify_code,
        )
        request_object = RequestFactory()
        request_object.session = rasb_client.session._get_session_from_db()
        self.request_object = request_object

    def test_email_verify_form_correct(self, rasb_client):
        form = EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert form.is_valid()

    def test_email_verify_form_incorrect_code(self, rasb_client):
        form = EmailVerifyForm(data={"email_verification_code": "1"}, request=self.request_object)
        assert not form.is_valid()
        assert "email_verification_code" in form.errors

    def test_email_verify_form_expired_code(self, rasb_client):
        self.obj.date_created = self.obj.date_created - timedelta(days=1)
        self.obj.save()
        form = EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert "email_verification_code" in form.errors
