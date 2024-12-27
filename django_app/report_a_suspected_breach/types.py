from typing import Literal, TypedDict


class ReporterDetails(TypedDict):
    full_name: str
    name_of_business_you_work_for: str
    professional_relationship: str
    email_address: str


class BreacherDetails(TypedDict):
    type_of_relationship: Literal["breacher"]
    name: str
    website: str
    registered_company_number: str
    email: str
    address_line_1: str
    address_line_2: str
    address_line_3: str
    address_line_4: str
    town_or_city: str
    country: str
    postal_code: str
    county: str
    additional_contact_details: str
