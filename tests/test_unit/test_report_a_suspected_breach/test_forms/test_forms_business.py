from unittest.mock import patch

from report_a_suspected_breach import choices
from report_a_suspected_breach.forms.forms_business import (
    AreYouReportingABusinessOnCompaniesHouseForm,
    DoYouKnowTheRegisteredCompanyNumberForm,
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
    @patch("report_a_suspected_breach.forms.forms_business.get_formatted_address")
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
