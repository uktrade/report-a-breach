import base64
from typing import Any

import requests
from django.conf import settings
from report_a_suspected_breach.exceptions import (
    CompaniesHouse500Error,
    CompaniesHouseException,
)

COMPANIES_HOUSE_BASE_DOMAIN = "https://api.companieshouse.gov.uk"


def get_companies_house_basic_auth_token(api_key: str = settings.COMPANIES_HOUSE_API_KEY) -> str:
    """
    Returns the basic auth token for Companies House API.
    """
    return base64.b64encode(bytes(f"{api_key}:", "utf-8")).decode("utf-8")


def get_details_from_companies_house(registration_number: str) -> dict[str, Any]:
    """
    Retrieves and returns details of a company from Companies House
    using registration number that is passed in.
    """

    get_company_headers = {"Authorization": f"Basic {get_companies_house_basic_auth_token()}"}
    response = requests.get(
        f"{COMPANIES_HOUSE_BASE_DOMAIN}/company/{registration_number}",
        headers=get_company_headers,
    )
    if response.status_code == 200:
        return response.json()

    if response.status_code == 500:
        raise CompaniesHouse500Error

    raise CompaniesHouseException(f"Companies House API request failed: {response.status_code}")
