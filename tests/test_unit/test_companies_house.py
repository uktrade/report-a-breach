import unittest
from unittest.mock import patch

from django.test import override_settings
from report_a_suspected_breach.exceptions import CompaniesHouseException

from django_app.utils.companies_house import (
    get_companies_house_basic_auth_token,
    get_details_from_companies_house,
    get_formatted_address,
)


class TestCompaniesHouse(unittest.TestCase):
    class MockGoodResponse:
        status_code = 200

        def json(*args):
            return {"company_number": "12345678", "name": "Test Company"}

    class MockBadResponse:
        status_code = 500

    @patch("requests.get", return_value=MockGoodResponse)
    def test_success_get_company(self, mocked_get):
        response = get_details_from_companies_house("12345678")
        assert response["company_number"] == "12345678"
        assert response["name"] == "Test Company"

    @patch("requests.get", return_value=MockBadResponse)
    def test_failure_get_company(self, mocked_get):
        with self.assertRaises(CompaniesHouseException):
            get_details_from_companies_house("12345678")

    @override_settings(COMPANIES_HOUSE_API_KEY="1234")
    def test_basic_auth_token(self):
        assert get_companies_house_basic_auth_token("1234") == "MTIzNDo="

    def test_get_formatted_address_outside_uk(self):
        address_dict = {
            "address_line_1": "123 Fake Street",
            "address_line_2": "Fake Town",
            "country": "DE",
            "postal_code": "AB12 3CD",
        }
        formatted_address = get_formatted_address(address_dict)
        assert formatted_address == "123 Fake Street,\n Fake Town,\n AB12 3CD,\n Germany"

    def test_get_formatted_address_uk(self):
        address_dict = {
            "address_line_1": "123 Fake Street",
            "address_line_2": "Fake Town",
            "country": "GB",
            "postal_code": "AB12 3CD",
        }
        formatted_address = get_formatted_address(address_dict)
        assert formatted_address == "123 Fake Street,\n Fake Town,\n AB12 3CD,\n United Kingdom"

    def test_get_formatted_address_no_line_2(self):
        address_dict = {
            "address_line_1": "123 Fake Street",
            "country": "GB",
            "postal_code": "AB12 3CD",
        }
        formatted_address = get_formatted_address(address_dict)
        assert formatted_address == "123 Fake Street,\n AB12 3CD,\n United Kingdom"

    def test_get_formatted_address_no_country(self):
        address_dict = {
            "address_line_1": "123 Fake Street",
            "address_line_2": "Fake Town",
            "postal_code": "AB12 3CD",
        }
        formatted_address = get_formatted_address(address_dict)
        assert formatted_address == "123 Fake Street,\n Fake Town,\n AB12 3CD"
