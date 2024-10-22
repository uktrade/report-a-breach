from datetime import timedelta

import pytest
from django import forms as django_forms
from django.test import RequestFactory
from report_a_suspected_breach import choices
from report_a_suspected_breach.forms.forms_start import (
    EmailForm,
    EmailVerifyForm,
    NameAndBusinessYouWorkForForm,
    NameForm,
    StartForm,
)
from report_a_suspected_breach.models import ReporterEmailVerification


class TestStartForm:
    def test_required(self):
        form = StartForm(data={"reporter_professional_relationship": None})
        assert not form.is_valid()
        assert "reporter_professional_relationship" in form.errors
        assert form.errors.as_data()["reporter_professional_relationship"][0].code == "required"

    def test_optional_choice_removed(self):
        form = StartForm()
        assert len(form.fields["reporter_professional_relationship"].choices) == len(
            choices.ReporterProfessionalRelationshipChoices.choices
        )

    def test_widget(self):
        form = StartForm()
        assert isinstance(form.fields["reporter_professional_relationship"].widget, django_forms.RadioSelect)


class TestEmailForm:
    def test_required(self):
        form = EmailForm(data={"reporter_email_address": None})
        assert not form.is_valid()
        assert "reporter_email_address" in form.errors
        assert form.errors.as_data()["reporter_email_address"][0].code == "required"

    def test_invalid(self):
        form = EmailForm(data={"reporter_email_address": "invalid"})
        assert not form.is_valid()
        assert "reporter_email_address" in form.errors
        assert form.errors.as_data()["reporter_email_address"][0].code == "invalid"


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
        request_object.method = "POST"
        self.request_object = request_object

    def test_email_verify_form_correct(self):
        form = EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert form.is_valid()

    def test_email_verify_form_incorrect_code(self):
        form = EmailVerifyForm(data={"email_verification_code": "1"}, request=self.request_object)
        assert not form.is_valid()
        assert "email_verification_code" in form.errors

    def test_email_verify_form_expired_code_2_hours(self):
        self.obj.date_created = self.obj.date_created - timedelta(days=1)
        self.obj.save()
        form = EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert form.has_error("email_verification_code", "invalid_after_expired")

    def test_email_verify_form_expired_code_30_minutes(self):
        self.obj.date_created = self.obj.date_created - timedelta(minutes=30)
        self.obj.save()
        form = EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert form.has_error("email_verification_code", "expired")


class TestNameForm:
    def test_required(self):
        form = NameForm(data={"reporter_full_name": None})
        assert not form.is_valid()
        assert "reporter_full_name" in form.errors
        assert form.errors.as_data()["reporter_full_name"][0].code == "required"


class TestNameAndBusinessYouWorkForForm:
    def test_reporter_full_name_required(self):
        form = NameAndBusinessYouWorkForForm(data={"reporter_full_name": None})
        assert not form.is_valid()
        assert "reporter_full_name" in form.errors
        assert form.errors.as_data()["reporter_full_name"][0].code == "required"

    def test_reporter_name_of_business_required(self):
        form = NameAndBusinessYouWorkForForm(data={"reporter_name_of_business_you_work_for": None})
        assert not form.is_valid()
        assert "reporter_name_of_business_you_work_for" in form.errors
        assert form.errors.as_data()["reporter_name_of_business_you_work_for"][0].code == "required"
