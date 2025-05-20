from unittest.mock import patch

from report_a_suspected_breach import choices
from report_a_suspected_breach.forms.forms_business import (
    AreYouReportingABusinessOnCompaniesHouseForm,
    BusinessOrPersonDetailsForm,
    DoYouKnowTheRegisteredCompanyNumberForm,
    ManualCompaniesHouseInputForm,
)


class TestAreYouReportingABusinessOnCompaniesHouseForm:
    def test_business_registered_on_companies_house_required(self):
        form = AreYouReportingABusinessOnCompaniesHouseForm(data={"business_registered_on_companies_house": None})
        assert not form.is_valid()
        assert "business_registered_on_companies_house" in form.errors
        assert form.errors.as_data()["business_registered_on_companies_house"][0].code == "required"

    def test_optional_choice_removed(self):
        form = AreYouReportingABusinessOnCompaniesHouseForm()
        assert len(form.fields["business_registered_on_companies_house"].choices) == len(choices.YesNoDoNotKnowChoices.choices)

    def test_init_method_removes_first_choice(self):
        original_form_choices = choices.YesNoDoNotKnowChoices.choices.copy()
        form = AreYouReportingABusinessOnCompaniesHouseForm()
        form.fields["business_registered_on_companies_house"].choices = [("", "Select one")] + list(original_form_choices)
        form.__init__()
        assert ("", "Select one") not in form.fields["business_registered_on_companies_house"].choices


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

    @patch("report_a_suspected_breach.forms.forms_business.get_details_from_companies_house")
    def test_clean(self, mocked_get_details_from_companies_house, request_object):
        mocked_get_details_from_companies_house.return_value = {
            "company_number": "12345678",
            "company_name": "Test Company",
            "registered_office_address": {
                "address_line_1": "12 road",
                "address_line_2": "Flat 3",
                "locality": "London",
                "postal_code": "E1 4UD",
                "country": "England",
            },
        }
        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["registered_company_name"] == "Test Company"
        assert cleaned_data["readable_address"] == "12 road,\n Flat 3,\n London,\n E1 4UD,\n United Kingdom"
        assert cleaned_data["country"] == "GB"
        assert cleaned_data["town_or_city"] == "London"
        assert cleaned_data["registered_company_number"] == "12345678"

    @patch("report_a_suspected_breach.forms.forms_business.get_details_from_companies_house")
    def test_clean_non_uk_company(self, mocked_get_details_from_companies_house, request_object):
        mocked_get_details_from_companies_house.return_value = {
            "company_number": "12345678",
            "company_name": "Test Company",
            "registered_office_address": {
                "address_line_1": "12 road",
                "address_line_2": "Flat 3",
                "locality": "Port Louis",
                "postal_code": "12345",
                "country": "Mauritius",
            },
        }
        form = DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["registered_company_name"] == "Test Company"
        assert cleaned_data["readable_address"] == "12 road,\n Flat 3,\n Port Louis,\n 12345,\n Mauritius"
        assert cleaned_data["country"] == "MU"
        assert cleaned_data["town_or_city"] == "Port Louis"
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


class TestManualCompaniesHouseInputForm:
    def test_form_layout(self):
        form = ManualCompaniesHouseInputForm(data={"manual_companies_house_input": None})
        assert not form.is_valid()
        assert "manual_companies_house_input" in form.errors
        expected_error = "Select if the address of the business suspected of breaching sanctions is in the UK, or outside the UK"
        assert form.errors["manual_companies_house_input"][0] == expected_error


class TestBusinessOrPersonDetailsForm:
    def test_form_layout(self):
        form = BusinessOrPersonDetailsForm()
        assert hasattr(form, "form_h1_header")
        assert form.form_h1_header == "Business or person details"
