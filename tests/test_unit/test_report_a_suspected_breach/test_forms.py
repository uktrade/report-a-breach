from datetime import timedelta
from unittest.mock import patch

import pytest
from django import forms as django_forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from report_a_suspected_breach import choices
from report_a_suspected_breach.forms.forms_a import (
    EmailForm,
    EmailVerifyForm,
    NameAndBusinessYouWorkForForm,
    NameForm,
    StartForm,
)
from report_a_suspected_breach.forms.forms_b import (
    AreYouReportingABusinessOnCompaniesHouseForm,
    DoYouKnowTheRegisteredCompanyNumberForm,
)
from report_a_suspected_breach.forms.forms_c import (
    WhenDidYouFirstSuspectForm,
    WhichSanctionsRegimeForm,
)
from report_a_suspected_breach.forms.forms_d import (
    AboutTheEndUserForm,
    ZeroEndUsersForm,
)
from report_a_suspected_breach.forms.forms_e import UploadDocumentsForm
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


class TestAreYouReportingABusinessOnCompaniesHouseForm:
    def test_business_registered_on_companies_house_required(self):
        form = AreYouReportingABusinessOnCompaniesHouseForm(data={"business_registered_on_companies_house": None})
        assert not form.is_valid()
        assert "business_registered_on_companies_house" in form.errors
        assert form.errors.as_data()["business_registered_on_companies_house"][0].code == "required"

    def test_optional_choice_removed(self):
        form = AreYouReportingABusinessOnCompaniesHouseForm()
        assert len(form.fields["business_registered_on_companies_house"].choices) == len(choices.YesNoDoNotKnowChoices.choices)


class TestDoYouKnowTheRegisteredCompanyNumberForm:
    def test_do_you_know_the_registered_company_number_required(self, request_object):
        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": None}, request=request_object
        )
        assert not form.is_valid()
        assert "do_you_know_the_registered_company_number" in form.errors
        assert form.errors.as_data()["do_you_know_the_registered_company_number"][0].code == "required"

    def test_registered_company_number_required(self, request_object):
        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": None}, request=request_object
        )
        assert not form.is_valid()
        assert "registered_company_number" in form.errors
        assert form.errors.as_data()["registered_company_number"][0].code == "required"

    def test_registered_company_number_not_required(self, request_object):
        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "no", "registered_company_number": None}, request=request_object
        )
        assert form.is_valid()

    @patch("report_a_suspected_breach.forms.forms_b.get_details_from_companies_house")
    @patch("report_a_suspected_breach.forms.forms_b.get_formatted_address")
    def test_clean(self, mocked_get_formatted_address, mocked_get_details_from_companies_house, request_object):
        mocked_get_details_from_companies_house.return_value = {
            "company_number": "12345678",
            "company_name": "Test Company",
            "registered_office_address": "",
        }
        mocked_get_formatted_address.return_value = "12 road, London"

        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["registered_company_name"] == "Test Company"
        assert cleaned_data["registered_office_address"] == "12 road, London"
        assert cleaned_data["registered_company_number"] == "12345678"

    def test_form_is_unbound(self, request_object):
        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        assert form.is_bound

        request_object.GET = {"change": "yes"}
        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        assert not form.is_bound


class TestWhenDidYouFirstSuspectForm:
    def get_date_post_dictionary(self, day: int | None, month: int | None, year: int | None):
        return {"when_did_you_first_suspect_0": day, "when_did_you_first_suspect_1": month, "when_did_you_first_suspect_2": year}

    def test_date_in_the_future(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 3000))
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert (
            form.errors.as_data()["when_did_you_first_suspect"][0].message
            == "The date you first suspected the breach must be in the past"
        )

    def test_year_prefixing(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 20))
        assert form.is_valid()
        assert form.cleaned_data["when_did_you_first_suspect"].year == 2020

    def test_too_short_year(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 400))
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert form.errors.as_data()["when_did_you_first_suspect"][0].code == "invalid"

    def test_incomplete(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, None))
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert form.errors.as_data()["when_did_you_first_suspect"][0].code == "incomplete"

    def test_is_the_date_accurate_required(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": None})
        assert not form.is_valid()
        assert "is_the_date_accurate" in form.errors
        assert form.errors.as_data()["is_the_date_accurate"][0].code == "required"


class TestAboutTheEndUserForm:
    def test_postal_code_validation(self):
        form = AboutTheEndUserForm(data={"postal_code": "SW1A 1AA"}, is_uk_address=True)
        assert form.is_valid()

        form = AboutTheEndUserForm(data={"postal_code": "123"}, is_uk_address=True)
        assert not form.is_valid()
        assert "postal_code" in form.errors
        assert form.errors.as_data()["postal_code"][0].code == "invalid"

    def test_clickable_website_url(self):
        form = AboutTheEndUserForm(data={"website": "example.com"})
        form.is_valid()
        assert form.cleaned_data["clickable_website_url"] == "https://example.com"

        form = AboutTheEndUserForm(data={"website": "https://example.com"})
        form.is_valid()
        assert form.cleaned_data["clickable_website_url"] == "https://example.com"

        form = AboutTheEndUserForm(data={"website": "https123://example.com"})
        form.is_valid()
        assert form.cleaned_data["clickable_website_url"] == "https123://example.com"


class TestZeroEndUsersForm:
    def test_do_you_want_to_add_an_end_user_validation(self):
        form = ZeroEndUsersForm(data={"do_you_want_to_add_an_end_user": True})
        assert form.is_valid()
        form = ZeroEndUsersForm(data={})
        assert not form.is_valid()
        assert "do_you_want_to_add_an_end_user" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_an_end_user"][0].code == "required"


class TestUploadDocumentsForm:
    class MockAllSessionFiles:
        def __init__(self, length: int = 0):
            self.length = length
            super().__init__()

        def __len__(self):
            return self.length

    def test_valid(self, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")

        form = UploadDocumentsForm(
            files={
                "document": [
                    good_file,
                ]
            },
            request=request_object,
        )
        assert form.is_valid()

    def test_invalid_mimetype(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"GIF8")

        form = UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "invalid_file_type"

    def test_invalid_extension(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"%PDF-test_pdf")

        form = UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "invalid_file_type"

    def test_too_large(self, request_object):
        large_file = SimpleUploadedFile("large.pdf", b"%PDF-test_pdf")
        large_file.size = 9999999999

        form = UploadDocumentsForm(
            files={
                "document": [
                    large_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "too_large"

    @patch("report_a_suspected_breach.forms.forms_e.get_all_session_files", return_value=MockAllSessionFiles(length=10))
    def test_too_many_uploaded(self, mocked_get_all_session_files, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")

        form = UploadDocumentsForm(
            files={
                "document": [
                    good_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "too_many"

    def test_invalid_extension_file_name_escaped(self, request_object):
        bad_file = SimpleUploadedFile("<img src=xonerror=alert(document.domain)>gif.gif", b"GIF8")

        form = UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].message == (
            "The selected file must be a DOC, DOCX, ODT, FODT, XLS, XLSX, ODS, FODS, PPT, PPTX, ODP, "
            "FODP, PDF, TXT, CSV, ZIP, HTML, JPEG, JPG or PNG"
        )


@pytest.mark.django_db
class TestWhichSanctionsRegimeForm:
    def test_required(self):
        form = WhichSanctionsRegimeForm(data={"which_sanctions_regime": None})
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.errors.as_data()["which_sanctions_regime"][0].code == "required"

    @patch(
        "report_a_suspected_breach.forms.forms_c.active_regimes",
        [
            {"name": "test regime", "is_active": True},
            {"name": "test regime1", "is_active": True},
            {"name": "test regime2", "is_active": True},
        ],
    )
    def test_choices_creation(self):
        form = WhichSanctionsRegimeForm()
        assert len(form.fields["which_sanctions_regime"].choices) == 5  # 3 + 2 default choices
        flat_choices = [choice[0] for choice in form.fields["which_sanctions_regime"].choices]
        assert "test regime" in flat_choices
        assert "test regime1" in flat_choices
        assert "test regime2" in flat_choices

        assert flat_choices[-1] == "Other Regime"
        assert flat_choices[-2] == "Unknown Regime"

    @patch(
        "report_a_suspected_breach.forms.forms_c.active_regimes",
        [
            {"name": "test regime", "is_active": True},
        ],
    )
    def test_assert_unknown_regime_selected_error(self):
        form = WhichSanctionsRegimeForm(data={"which_sanctions_regime": ["Unknown Regime", "test regime"]})
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.errors.as_data()["which_sanctions_regime"][0].code == "invalid"

    @patch(
        "report_a_suspected_breach.forms.forms_c.active_regimes",
        [
            {"name": "test regime", "is_active": True},
        ],
    )
    def test_assert_other_regime_selected_error(self):
        form = WhichSanctionsRegimeForm(data={"which_sanctions_regime": ["Other Regime", "test regime"]})
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.errors.as_data()["which_sanctions_regime"][0].code == "invalid"
