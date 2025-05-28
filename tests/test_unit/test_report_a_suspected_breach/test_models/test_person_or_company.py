import pytest
from django.core.exceptions import ValidationError
from report_a_suspected_breach.models import PersonOrCompany

from tests.factories import BreacherPersonOrCompanyFactory


def test_save_person_or_company_name_of_business(breach_object):
    #  Test the save_person_or_company method.
    new_object = PersonOrCompany.save_person_or_company(
        type_of_report=breach_object,
        person_or_company={
            "name": "Test Name",
            "website": "https://www.test.com",
            "email": "test@example.com",
            "additional_contact_information": "Test additional contact information",
            "do_you_know_the_registered_company_number": "yes",
            "registered_company_name": "Test Registered Company Name",
            "name_of_business": "Test Registered Company Name 0",
            "address_line_1": "Test Address Line 1",
            "address_line_2": "Test Address Line 2",
            "town_or_city": "Test Town or City",
            "country": "GB",
        },
        relationship="recipient",
    )
    assert new_object.name == "Test Name"
    assert new_object.name_of_business == "Test Registered Company Name"

    new_object = PersonOrCompany.save_person_or_company(
        type_of_report=breach_object,
        person_or_company={
            "name": "Test Name",
            "website": "https://www.test.com",
            "email": "test@example.com",
            "additional_contact_information": "Test additional contact information",
            "registered_company_name": "Test Registered Company Name",
            "name_of_business": "Test Registered Company Name 0",
            "address_line_1": "Test Address Line 1",
            "address_line_2": "Test Address Line 2",
            "town_or_city": "Test Town or City",
            "country": "GB",
        },
        relationship="recipient",
    )
    assert new_object.name == "Test Name"
    assert new_object.name_of_business == "Test Registered Company Name 0"


def test_readable_address(breach_object):
    company = BreacherPersonOrCompanyFactory(
        registered_office_address="12 test road, coventry, GL123, United Kingdom",
        address_line_1="DO NOT SHOW",
        address_line_2="DO NOT SHOW",
        breach_report=breach_object,
    )
    assert company.get_readable_address() == "12 test road, coventry, GL123, United Kingdom"

    company = BreacherPersonOrCompanyFactory(
        registered_office_address=None, address_line_1="12 test road", address_line_2="coventry", breach_report=breach_object
    )
    assert company.get_readable_address() == "12 test road,\n coventry"


def test_save_person_or_company_raises_validation_error(breach_object):
    with pytest.raises(ValidationError) as err:
        PersonOrCompany.save_person_or_company(
            type_of_report=None,
            person_or_company={
                "name": "Test Name",
                "website": "https://www.test.com",
                "email": "test@example.com",
                "additional_contact_information": "Test additional contact information",
                "registered_company_name": "Test Registered Company Name",
                "name_of_business": "Test Registered Company Name 0",
                "address_line_1": "Test Address Line 1",
                "address_line_2": "Test Address Line 2",
                "town_or_city": "Test Town or City",
                "country": "GB",
            },
            relationship="recipient",
        )

    assert err.value.messages[0] == "Unrecognized report type: NoneType"


def test_save_person_or_company_whistleblower_report(whistleblower_report_object):
    new_object = PersonOrCompany.save_person_or_company(
        type_of_report=whistleblower_report_object,
        person_or_company={
            "name": "Test Name",
            "website": "https://www.test.com",
            "email": "test@example.com",
            "additional_contact_information": "Test additional contact information",
            "do_you_know_the_registered_company_number": "yes",
            "registered_company_name": "Test Registered Company Name",
            "name_of_business": "Test Registered Company Name 0",
            "address_line_1": "Test Address Line 1",
            "address_line_2": "Test Address Line 2",
            "town_or_city": "Test Town or City",
            "country": "GB",
        },
        relationship="recipient",
    )
    assert new_object.whistleblower_report == whistleblower_report_object
