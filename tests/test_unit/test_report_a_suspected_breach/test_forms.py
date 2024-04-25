from datetime import timedelta
from unittest.mock import patch

import pytest
from django import forms as django_forms
from django.test import RequestFactory
from report_a_suspected_breach import choices, forms
from report_a_suspected_breach.models import ReporterEmailVerification


class TestStartForm:
    def test_required(self):
        form = forms.StartForm(data={"reporter_professional_relationship": None})
        assert not form.is_valid()
        assert "reporter_professional_relationship" in form.errors
        assert form.errors.as_data()["reporter_professional_relationship"][0].code == "required"

    def test_optional_choice_removed(self):
        form = forms.StartForm()
        assert len(form.fields["reporter_professional_relationship"].choices) == len(
            choices.ReporterProfessionalRelationshipChoices.choices
        )

    def test_widget(self):
        form = forms.StartForm()
        assert isinstance(form.fields["reporter_professional_relationship"].widget, django_forms.RadioSelect)


class TestEmailForm:
    def test_required(self):
        form = forms.EmailForm(data={"reporter_email_address": None})
        assert not form.is_valid()
        assert "reporter_email_address" in form.errors
        assert form.errors.as_data()["reporter_email_address"][0].code == "required"

    def test_invalid(self):
        form = forms.EmailForm(data={"reporter_email_address": "invalid"})
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
        self.request_object = request_object

    def test_email_verify_form_correct(self, rasb_client):
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert form.is_valid()

    def test_email_verify_form_incorrect_code(self, rasb_client):
        form = forms.EmailVerifyForm(data={"email_verification_code": "1"}, request=self.request_object)
        assert not form.is_valid()
        assert "email_verification_code" in form.errors

    def test_email_verify_form_expired_code(self, rasb_client):
        self.obj.date_created = self.obj.date_created - timedelta(days=1)
        self.obj.save()
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert "email_verification_code" in form.errors


class TestNameForm:
    def test_required(self):
        form = forms.NameForm(data={"reporter_full_name": None})
        assert not form.is_valid()
        assert "reporter_full_name" in form.errors
        assert form.errors.as_data()["reporter_full_name"][0].code == "required"


class TestNameAndBusinessYouWorkForForm:
    def test_reporter_full_name_required(self):
        form = forms.NameAndBusinessYouWorkForForm(data={"reporter_full_name": None})
        assert not form.is_valid()
        assert "reporter_full_name" in form.errors
        assert form.errors.as_data()["reporter_full_name"][0].code == "required"

    def test_reporter_name_of_business_required(self):
        form = forms.NameAndBusinessYouWorkForForm(data={"reporter_name_of_business_you_work_for": None})
        assert not form.is_valid()
        assert "reporter_name_of_business_you_work_for" in form.errors
        assert form.errors.as_data()["reporter_name_of_business_you_work_for"][0].code == "required"


class TestAreYouReportingABusinessOnCompaniesHouseForm:
    def test_business_registered_on_companies_house_required(self):
        form = forms.AreYouReportingABusinessOnCompaniesHouseForm(data={"business_registered_on_companies_house": None})
        assert not form.is_valid()
        assert "business_registered_on_companies_house" in form.errors
        assert form.errors.as_data()["business_registered_on_companies_house"][0].code == "required"

    def test_optional_choice_removed(self):
        form = forms.AreYouReportingABusinessOnCompaniesHouseForm()
        assert len(form.fields["business_registered_on_companies_house"].choices) == len(choices.YesNoDoNotKnowChoices.choices)


class TestDoYouKnowTheRegisteredCompanyNumberForm:
    def test_do_you_know_the_registered_company_number_required(self):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(data={"do_you_know_the_registered_company_number": None})
        assert not form.is_valid()
        assert "do_you_know_the_registered_company_number" in form.errors
        assert form.errors.as_data()["do_you_know_the_registered_company_number"][0].code == "required"

    def test_registered_company_number_required(self):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": None}
        )
        assert not form.is_valid()
        assert "registered_company_number" in form.errors
        assert form.errors.as_data()["registered_company_number"][0].code == "required"

    def test_registered_company_number_not_required(self):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "no", "registered_company_number": None}
        )
        assert form.is_valid()

    @patch("report_a_suspected_breach.forms.get_details_from_companies_house")
    @patch("report_a_suspected_breach.forms.get_formatted_address")
    def test_clean(self, mocked_get_formatted_address, mocked_get_details_from_companies_house, request_object):
        mocked_get_details_from_companies_house.return_value = {
            "company_number": "12345678",
            "company_name": "Test Company",
            "registered_office_address": "",
        }
        mocked_get_formatted_address.return_value = "12 road, London"

        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["registered_company_name"] == "Test Company"
        assert cleaned_data["registered_office_address"] == "12 road, London"
        assert cleaned_data["registered_company_number"] == "12345678"

    def test_clean_from_session(self, request_object):
        """Tests that if the session contacts company details, the form will use those instead"""
        request_object.session["company_details"] = {
            "registered_company_name": "Test Company",
            "registered_office_address": "12 road, London",
            "registered_company_number": "12345678",
        }

        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["registered_company_name"] == "Test Company"
        assert cleaned_data["registered_office_address"] == "12 road, London"
        assert cleaned_data["registered_company_number"] == "12345678"


class TestWhenDidYouFirstSuspectForm:
    def get_date_post_dictionary(self, day: int | None, month: int | None, year: int | None):
        return {"when_did_you_first_suspect_0": day, "when_did_you_first_suspect_1": month, "when_did_you_first_suspect_2": year}

    def test_date_in_the_future(self):
        form = forms.WhenDidYouFirstSuspectForm(
            data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 3000)
        )
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert (
            form.errors.as_data()["when_did_you_first_suspect"][0].message
            == "The date you first suspected the breach must be in the past"
        )

    def test_year_prefixing(self):
        form = forms.WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 20))
        assert form.is_valid()
        assert form.cleaned_data["when_did_you_first_suspect"].year == 2020

    def test_too_short_year(self):
        form = forms.WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 400))
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert form.errors.as_data()["when_did_you_first_suspect"][0].code == "invalid"

    def test_incomplete(self):
        form = forms.WhenDidYouFirstSuspectForm(
            data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, None)
        )
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert form.errors.as_data()["when_did_you_first_suspect"][0].code == "incomplete"

    def test_is_the_date_accurate_required(self):
        form = forms.WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": None})
        assert not form.is_valid()
        assert "is_the_date_accurate" in form.errors
        assert form.errors.as_data()["is_the_date_accurate"][0].code == "required"


class TestAboutTheEndUserForm:
    def test_postal_code_validation(self):
        form = forms.AboutTheEndUserForm(data={"postal_code": "SW1A 1AA"}, is_uk_address=True)
        assert form.is_valid()

        form = forms.AboutTheEndUserForm(data={"postal_code": "123"}, is_uk_address=True)
        assert not form.is_valid()
        assert "postal_code" in form.errors
        assert form.errors.as_data()["postal_code"][0].code == "invalid"
