import os

from report_a_suspected_breach.utils import get_active_regimes

EMAIL_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "012345"}
UK_ADDRESS_DETAILS = {
    "name": "business",
    "website": "example.com",
    "address_line_1": "A1",
    "address_line_2": "A2",
    "town": "Town",
    "county": "County",
    "postcode": "AA00AA",
}

NON_UK_ADDRESS_DETAILS = {
    "name": "business",
    "website": "example.com",
    "address_line_1": "A1",
    "address_line_2": "A2",
    "address_line_3": "A3",
    "address_line_4": "A4",
    "town": "Town",
    "county": "County",
    "country": "DE",
}

UK_BREACHER_ADDRESS_DETAILS = {
    "name": "Breacher",
    "website": "breacher.com",
    "address_line_1": "Breach Lane",
    "address_line_2": "Breach Avenue",
    "town": "Breach Town",
    "county": "Breach County",
    "postcode": "BB00BB",
}

NON_UK_BREACHER_ADDRESS_DETAILS = {
    "name": "German Breacher",
    "website": "germanbreacher.com",
    "address_line_1": "Germany Lane",
    "address_line_2": "Germany Avenue",
    "address_line_3": "Line 3 Germany",
    "address_line_4": "Line 4 Germany",
    "town": "Germany Town",
    "country": "DE",
}

UK_SUPPLIER_ADDRESS_DETAILS = {
    "name": "Supplier",
    "website": "supplier.com",
    "address_line_1": "Supply Street",
    "address_line_2": "Supply Lane",
    "town": "Supply Town",
    "county": "Supply County",
    "postcode": "SU00SU",
}

NON_UK_SUPPLIER_ADDRESS_DETAILS = {
    "name": "supplier",
    "website": "supplier.com",
    "address_line_1": "Supply Street",
    "address_line_2": "Supply Lane",
    "address_line_3": "Supply A3",
    "address_line_4": "Supply A4",
    "town": "Town",
    "county": "County",
    "country": "DE",
}

SANCTIONS = [sanction["name"] for sanction in get_active_regimes()]

FILES = [os.path.join(os.path.dirname(__file__), "test_report_a_suspected_breach/testfiles/testfile.pdf")]
MISSING_FILE_TYPE = [os.path.join(os.path.dirname(__file__), "test_report_a_suspected_breach/testfiles/missing_filetype")]
MALWARE_FILE_TYPE = [os.path.join(os.path.dirname(__file__), "test_report_a_suspected_breach/testfiles/mock_malware_file.txt")]
INCORRECT_EXTENSION_FILE_TYPE = [
    os.path.join(os.path.dirname(__file__), "test_report_a_suspected_breach/testfiles/incorrect_file_extension.sh")
]

END_USERS = {
    "end_user1": {
        "location": "The UK",
        "name": "End User1",
        "business": "",
        "email": "",
        "website": "",
        "address_line_1": "AL1",
        "address_line_2": "AL2",
        "town_or_city": "Town",
        "county": "Lothian",
        "postcode": "EU12EU",
        "additional_contact_details": "",
    },
    "end_user2": {
        "location": "Outside the UK",
        "name": "End User2",
        "business": "",
        "email": "",
        "website": "",
        "address_line_1": "AL1",
        "address_line_2": "",
        "address_line_3": "",
        "address_line_4": "",
        "town_or_city": "",
        "country": "UG",
        "additional_contact_details": "",
    },
    "end_user3": {
        "location": "Outside the UK",
        "name": "End User3",
        "business": "Business 3",
        "email": "email3@gmail.com",
        "website": "web.3.com",
        "address_line_1": "High St",
        "address_line_2": "Shoreham",
        "address_line_3": "Winder",
        "address_line_4": "",
        "town_or_city": "Usser",
        "country": "HU",
        "additional_contact_details": "",
    },
    "end_user4": {
        "location": "Outside the UK",
        "name": "End User4",
        "business": "Business 4",
        "email": "email4@gmail.com",
        "website": "web.4.com",
        "address_line_1": "Otto St",
        "address_line_2": "Mercury Lane",
        "address_line_3": "Holyrood",
        "address_line_4": "",
        "town_or_city": "Suva",
        "country": "FJ",
        "additional_contact_details": "",
    },
}
