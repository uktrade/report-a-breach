import unittest
from unittest.mock import patch

from django.test import override_settings

from report_a_breach.exceptions import CompaniesHouseException
from report_a_breach.utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)


class TestCompaniesHouse(unittest.TestCase):
    class MockGoodResponse:
        status_code = 200

        def json(self):
            return {"company_number": "12345678", "name": "Test Company"}

    class MockBadResponse:
        status_code = 500

    @patch("requests.get", return_value=MockGoodResponse)
    def test_success_get_company(self):
        response = get_details_from_companies_house("12345678")
        assert response["company_number"] == "12345678"
        assert response["name"] == "Test Company"

    @patch("requests.get", return_value=MockBadResponse)
    def test_failure_get_company(self):
        with self.assertRaises(CompaniesHouseException):
            get_details_from_companies_house("12345678")

    @override_settings(COMPANIES_HOUSE_API_KEY="1234")
    def test_basic_auth_token(self):
        from report_a_breach.utils.companies_house import COMPANIES_HOUSE_BASIC_AUTH

        assert COMPANIES_HOUSE_BASIC_AUTH == "MTIzNA=="

    def get_formatted_address(self):
        address_dict = {
            "address_line_1": "123 Fake Street",
            "address_line_2": "Fake Town",
            "country": "Fake Country",
            "postal_code": "AB12 3CD",
        }
        formatted_address = get_formatted_address(address_dict)
        assert formatted_address == "123 Fake Street, Fake Town, Fake Country, AB12 3CD"

    def get_formatted_address_no_line_2(self):
        address_dict = {
            "address_line_1": "123 Fake Street",
            "country": "Fake Country",
            "postal_code": "AB12 3CD",
        }
        formatted_address = get_formatted_address(address_dict)
        assert formatted_address == "123 Fake Street, Fake Country, AB12 3CD"

    def get_formatted_address_no_country(self):
        address_dict = {
            "address_line_1": "123 Fake Street",
            "address_line_2": "Fake Town",
            "postal_code": "AB12 3CD",
        }
        with self.assertRaises(KeyError):
            get_formatted_address(address_dict)
