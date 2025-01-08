from utils.address_formatter import turn_companies_house_into_normal_address_dict


def test_turn_companies_house_into_normal_address_dict():
    companies_house_address_dict = {
        "address_line_1": "Buckingham Palace",
        "address_line_2": "Address Line 2",
        "country": "United Kingdom",
        "locality": "London",
        "postal_code": "ER3 SOS",
    }
    normal_dict = turn_companies_house_into_normal_address_dict(companies_house_address_dict)
    assert normal_dict == {
        "address_line_1": "Buckingham Palace",
        "address_line_2": "Address Line 2",
        "country": "GB",
        "locality": "London",
        "postal_code": "ER3 SOS",
        "town_or_city": "London",
    }

    # now checking no country
    companies_house_address_dict = {
        "address_line_1": "Buckingham Palace",
        "address_line_2": "Address Line 2",
        "locality": "London",
        "postal_code": "ER3 SOS",
    }
    normal_dict = turn_companies_house_into_normal_address_dict(companies_house_address_dict)
    # it should default to GB
    assert normal_dict == {
        "address_line_1": "Buckingham Palace",
        "address_line_2": "Address Line 2",
        "country": "GB",
        "locality": "London",
        "postal_code": "ER3 SOS",
        "town_or_city": "London",
    }

    # now checking no locality
    companies_house_address_dict = {
        "address_line_1": "Buckingham Palace",
        "address_line_2": "Address Line 2",
        "country": "United Kingdom",
        "postal_code": "ER3 SOS",
    }
    normal_dict = turn_companies_house_into_normal_address_dict(companies_house_address_dict)
    # it should default to an empty string
    assert normal_dict == {
        "address_line_1": "Buckingham Palace",
        "address_line_2": "Address Line 2",
        "country": "GB",
        "postal_code": "ER3 SOS",
        "town_or_city": "",
    }
