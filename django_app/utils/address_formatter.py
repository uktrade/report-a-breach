"""Collection of functions to standardise and format address data"""

from typing import Any, Dict, TypedDict

from django_countries import countries


class AddressData(TypedDict):
    address_line_1: str
    address_line_2: str
    town_or_city: str
    postal_code: str
    country: str  # ISO 3166-1 alpha-2 code


# we place this outside the functions as it's fairly costly and won't change
country_name_to_code = {name: code for code, name in countries}


def turn_companies_house_into_normal_address_dict(address_dict: Dict[str, Any]) -> AddressData:
    new_address_dict = address_dict.copy()

    # companies house returns a whole country name, we need to convert it to a country code
    if country := address_dict.get("country"):
        # special case for UK
        if country in ["England", "Northern Ireland", "Scotland", "Wales", "United Kingdom", "England/Wales"]:
            new_address_dict["country"] = "GB"
        else:
            new_address_dict["country"] = country_name_to_code[country]
    else:
        # companies house doesn't always return a country, so we just assume GB if it's missing
        new_address_dict["country"] = "GB"

    # companies house uses locality for town_or_city (only sometimes though...)
    try:
        new_address_dict["town_or_city"] = address_dict["locality"]
    except KeyError:
        pass

    return new_address_dict


def get_formatted_address(address_dict: AddressData) -> str:
    """Get formatted, human-readable address from an AddressData address dict"""
    address_string = ""

    if line_1 := address_dict.get("address_line_1"):
        address_string += line_1

    if line_2 := address_dict.get("address_line_2"):
        address_string += f",\n {line_2}"

    if town_or_city := address_dict.get("town_or_city"):
        address_string += f",\n {town_or_city}"

    if postal_code := address_dict.get("postal_code"):
        address_string += f",\n {postal_code}"

    if country_code := address_dict.get("country"):
        country = countries.name(country_code)
        address_string += f",\n {country}"

    return address_string
