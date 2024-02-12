import base64

import requests
from django.conf import settings

COMPANIES_HOUSE_BASIC_AUTH = base64.b64encode(  # /PS-IGNORE
    bytes(f"{settings.COMPANIES_HOUSE_API_KEY}:", "utf-8")
).decode("utf-8")
COMPANIES_HOUSE_BASE_DOMAIN = "https://api.companieshouse.gov.uk"


class CompaniesHouseApi:
    def get_details_from_companies_house(self, registration_number):
        """
        Retrieves and returns details of a company from Companies House
        using registration number that is passed in.
        """

        if registration_number:
            headers_get_company = {"Authorization": f"Basic {COMPANIES_HOUSE_BASIC_AUTH}"}
            response = requests.get(
                f"{COMPANIES_HOUSE_BASE_DOMAIN}/company/{registration_number}",
                headers=headers_get_company,
            )
            if response.status_code == 200:
                return response.json()
        return {}
