import datetime

verify_code = "123456"

cleaned_data = {
    "start": {"reporter_professional_relationship": "third_party"},
    "email": {"reporter_email_address": "test@digital.trade.gov.uk"},
    "verify": {"email_verification_code": verify_code},
    "name": {"reporter_full_name": "john doe", "reporter_name_of_business_you_work_for": "jd ltd"},
    "business_or_person_details": {
        "name": "Test",
        "website": "http://jd.com",
        "country": "GB",
        "address_line_1": "AL1",
        "town_or_city": "Town",
        "postal_code": "NP8 8PD",
    },
    "are_you_reporting_a_business_on_companies_house": {"business_registered_on_companies_house": "no"},
    "do_you_know_the_registered_company_number": {"do_you_know_the_registered_company_number": "no"},
    "when_did_you_first_suspect": {
        "when_did_you_first_suspect": datetime.date(1994, 3, 12),
        "is_the_date_accurate": "approximate",
    },
    "what_were_the_goods": {"what_were_the_goods": "accountancy"},
    "where_were_the_goods_supplied_from": {"where_were_the_goods_supplied_from": "outside_the_uk"},
    "about_the_supplier": {
        "name": "Hampshire",
        "website": "http://hampshire.com",
        "country": "AX",
        "address_line_1": "AL1",
        "town_or_city": "Town",
    },
    "where_were_the_goods_supplied_to": {"where_were_the_goods_supplied_to": "outside_the_uk"},
    "were_there_other_addresses_in_the_supply_chain": {
        "were_there_other_addresses_in_the_supply_chain": "yes",
        "other_addresses_in_the_supply_chain": "These are some other address details",
    },
    "which_sanctions_regime": {"which_sanctions_regime": []},
    "tell_us_about_the_suspected_breach": {"tell_us_about_the_suspected_breach": "The breach was about accountancy"},
}

cleaned_companies_house_data = {
    "start": {"reporter_professional_relationship": "third_party"},
    "email": {"reporter_email_address": "test@digital.trade.gov.uk"},
    "verify": {"email_verification_code": verify_code},
    "name": {"reporter_full_name": "john doe", "reporter_name_of_business_you_work_for": "jd ltd"},
    "are_you_reporting_a_business_on_companies_house": {"business_registered_on_companies_house": "yes"},
    "do_you_know_the_registered_company_number": {
        "do_you_know_the_registered_company_number": "yes",
        "registered_company_number": 12345678,
        "registered_company_name": "LTD",
        "registered_office_address": "Hello",
    },
    "when_did_you_first_suspect": {
        "when_did_you_first_suspect": datetime.date(1994, 3, 12),
        "is_the_date_accurate": "approximate",
    },
    "what_were_the_goods": {"what_were_the_goods": "accountancy"},
    "where_were_the_goods_supplied_from": {"where_were_the_goods_supplied_from": "outside_the_uk"},
    "about_the_supplier": {
        "name": "Hampshire",
        "website": "http://hampshire.com",
        "country": "AX",
        "address_line_1": "AL1",
        "town_or_city": "Town",
    },
    "where_were_the_goods_supplied_to": {"where_were_the_goods_supplied_to": "outside_the_uk"},
    "were_there_other_addresses_in_the_supply_chain": {
        "were_there_other_addresses_in_the_supply_chain": "yes",
        "other_addresses_in_the_supply_chain": "These are some other address details",
    },
    "tell_us_about_the_suspected_breach": {"tell_us_about_the_suspected_breach": "The breach was about accountancy"},
}

end_users = {
    "end_user1": {"cleaned_data": {"name": "End User1", "country": "AX", "address_line_1": "AL1", "town_or_city": "Town"}},
    "end_user2": {
        "cleaned_data": {
            "name": "End User2",
            "website": "http://fdas.com",
            "country": "GB",
            "address_line_1": "Line 1",
            "town_or_city": "City",
        }
    },
    "end_user3": {"cleaned_data": {"name": "End User3", "address_line_1": "Address 1", "town_or_city": "town3", "country": "NZ"}},
}


person_or_company = {
    "name": "Test Company",
    "country": "GB",
    "address_line_1": "Address 1",
    "town_or_city": "Big Town",
    "postal_code": "NP8 8PD",
}
