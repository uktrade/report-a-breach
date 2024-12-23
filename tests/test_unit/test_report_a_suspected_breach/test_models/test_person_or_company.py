from report_a_suspected_breach.models import PersonOrCompany


def test_save_person_or_company_name_of_business(breach_object):
    #  Test the save_person_or_company method.
    new_object = PersonOrCompany.save_person_or_company(
        breach=breach_object,
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
        breach=breach_object,
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
