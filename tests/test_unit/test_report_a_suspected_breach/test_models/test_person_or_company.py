from tests.factories import BreacherPersonOrCompanyFactory


def test_readable_address(breach_object):
    company = BreacherPersonOrCompanyFactory(
        registered_office_address="12 test road, coventry, GL123, United Kingdom",
        address_line_1="DO NOT SHOW",
        address_line_2="DO NOT SHOW",
        breach=breach_object,
    )
    assert company.get_readable_address() == "12 test road, coventry, GL123, United Kingdom"

    company = BreacherPersonOrCompanyFactory(
        registered_office_address=None, address_line_1="12 test road", address_line_2="coventry", breach=breach_object
    )
    assert company.get_readable_address() == "12 test road,\n coventry"
