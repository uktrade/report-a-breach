import datetime
import uuid
from unittest.mock import patch

import pytest
from report_a_suspected_breach.exceptions import EmailNotVerifiedException
from report_a_suspected_breach.models import Breach, ReporterEmailVerification


def test_breach_reference(breach_object):
    breach_object.reference = None
    assert not breach_object.reference
    breach_object.assign_reference()
    assert breach_object.reference
    assert len(breach_object.reference) == 6


class TestCreateFromSession:
    basic_create_dict = {
        "start": {"reporter_professional_relationship": "owner"},
        "email": {"reporter_email_address": "test@example.com"},
        "name": {"reporter_full_name": "Chris P"},
        "are_you_reporting_a_business_on_companies_house": {"business_registered_on_companies_house": "yes"},
        "do_you_know_the_registered_company_number": {
            "do_you_know_the_registered_company_number": "yes",
            "registered_company_number": "0000001",
            "registered_company_name": "Test Company Name",
            "registered_office_address": "",
            "name": "Test Company Name",
            "address_line_1": "Buckingham Palace",
            "address_line_2": "Westminster",
            "country": "GB",
            "locality": "London",
            "postal_code": "SW1A 1AA",
            "town_or_city": "London",
            "readable_address": "Buckingham Palace, Westminster, London, SW1A 1AA",
        },
        "manual_companies_house_input": {},
        "check_company_details": {},
        "where_is_the_address_of_the_business_or_person": {},
        "business_or_person_details": {
            "name": "Test Company Name",
            "website": "https://www.example.com",
            "country": "GB",
            "town_or_city": "London",
            "address_line_1": "Buckingham Palace",
            "address_line_2": "Westminster",
        },
        "when_did_you_first_suspect": {"when_did_you_first_suspect": datetime.date(2014, 1, 1), "is_the_date_accurate": "exact"},
        "which_sanctions_regime": {"which_sanctions_regime": ["Other Regime"]},
        "what_were_the_goods": {"what_were_the_goods": "test"},
        "where_were_the_goods_supplied_from": {"where_were_the_goods_supplied_from": "same_address"},
        "about_the_supplier": {},
        "where_were_the_goods_made_available_from": {},
        "where_were_the_goods_made_available_to": {},
        "where_were_the_goods_made_available_to_end_user_uuid": {},
        "where_were_the_goods_supplied_to_end_user_uuid": {},
        "where_were_the_goods_supplied_to": {"where_were_the_goods_supplied_to": "i_do_not_know"},
        "were_there_other_addresses_in_the_supply_chain": {
            "were_there_other_addresses_in_the_supply_chain": "no",
            "other_addresses_in_the_supply_chain": "",
        },
        "upload_documents": {"document": []},
        "tell_us_about_the_suspected_breach": {"tell_us_about_the_suspected_breach": "test"},
    }

    @patch("report_a_suspected_breach.models.show_name_and_business_you_work_for_page")
    def test_get_reporter_details(self, patched_show_name_and_business_you_work_for_page, request_object):
        patched_show_name_and_business_you_work_for_page.return_value = True

        cleaned_data = {
            "name_and_business_you_work_for": {
                "reporter_full_name": "This is my name",
                "reporter_name_of_business_you_work_for": "Org I work for",
            },
            "start": {"reporter_professional_relationship": "owner"},
            "email": {"reporter_email_address": "test@example.com"},
        }
        reporter = Breach.get_reporter_details(cleaned_data, request_object)
        assert reporter["full_name"] == "This is my name"
        assert reporter["name_of_business_you_work_for"] == "Org I work for"
        assert reporter["email_address"] == "test@example.com"
        assert reporter["professional_relationship"] == "owner"

        # now for the other journey(s)
        patched_show_name_and_business_you_work_for_page.return_value = False
        cleaned_data = {
            "name": {"reporter_full_name": "Cool Guy"},
            "business_or_person_details": {"name": "Cool Guy Ltd"},
            "start": {"reporter_professional_relationship": "third_party"},
            "email": {"reporter_email_address": "test@example.com"},
        }
        reporter = Breach.get_reporter_details(cleaned_data, request_object)
        assert reporter["full_name"] == "Cool Guy"
        assert reporter["name_of_business_you_work_for"] == "Cool Guy Ltd"

        cleaned_data = {
            "name": {"reporter_full_name": "Mr Mouse"},
            "do_you_know_the_registered_company_number": {
                "do_you_know_the_registered_company_number": "yes",
                "registered_company_name": "Mr Mouse Inc",
            },
            "start": {"reporter_professional_relationship": "owner"},
            "email": {"reporter_email_address": "test@example.com"},
        }
        reporter = Breach.get_reporter_details(cleaned_data, request_object)
        assert reporter["full_name"] == "Mr Mouse"
        assert reporter["name_of_business_you_work_for"] == "Mr Mouse Inc"

    @patch("report_a_suspected_breach.models.Breach.get_reporter_details")
    @patch("report_a_suspected_breach.models.Breach.get_email_verification_object")
    @patch("report_a_suspected_breach.models.get_all_cleaned_data")
    def test_cant_progress_without_email_verification(
        self, get_all_cleaned_data, patched_get_email_verification_object, patched_get_reporter_details, request_object
    ):
        patched_get_reporter_details.return_value = {
            "full_name": "Chris",
            "name_of_business_you_work_for": "DBT",
            "email_address": "test@example.com",
        }
        patched_get_email_verification_object.return_value = ReporterEmailVerification.objects.create(
            email_verification_code="012345", verified=False
        )
        get_all_cleaned_data.return_value = self.basic_create_dict

        with pytest.raises(EmailNotVerifiedException):
            Breach.create_from_session(request_object)

    @patch("report_a_suspected_breach.forms.forms_business.get_details_from_companies_house")
    def test_get_breacher_details(self, patched_get_details_from_companies_house, request_object):
        session = request_object.session
        session["do_you_know_the_registered_company_number"] = {
            "do_you_know_the_registered_company_number": "yes",
            "registered_company_number": "00000001",
        }
        session["are_you_reporting_a_business_on_companies_house"] = {"business_registered_on_companies_house": "yes"}
        session.save()

        patched_get_details_from_companies_house.return_value = {
            "company_number": "00000001",
            "company_name": "Test Company Name",
            "registered_office_address": {
                "address_line_1": "Buckingham Palace",
                "address_line_2": "Westminster",
                "country": "England",
            },
        }

        cleaned_data = {
            "do_you_know_the_registered_company_number": {
                "do_you_know_the_registered_company_number": "yes",
                "registered_company_number": "000001",
                "name": "Test Company Name",
                "address_line_1": "Buckingham Palace",
                "address_line_2": "Westminster",
                "country": "GB",
            }
        }

        breacher = Breach.get_breacher_details(request_object, cleaned_data)
        assert breacher["registered_company_number"] == "000001"
        assert breacher["name"] == "Test Company Name"
        assert breacher["address_line_1"] == "Buckingham Palace"
        assert breacher["address_line_2"] == "Westminster"
        assert breacher["country"] == "GB"

        # now for the other journey(s)
        session["do_you_know_the_registered_company_number"] = {}
        session["are_you_reporting_a_business_on_companies_house"] = {"business_registered_on_companies_house": "mp"}
        session.save()

        cleaned_data = {
            "business_or_person_details": {
                "registered_company_number": "000002",
                "name": "Custom Company Name",
                "address_line_1": "The Shard",
                "address_line_2": "Westminster",
                "country": "GB",
            }
        }
        breacher = Breach.get_breacher_details(request_object, cleaned_data)
        assert breacher["registered_company_number"] == "000002"
        assert breacher["name"] == "Custom Company Name"
        assert breacher["address_line_1"] == "The Shard"
        assert breacher["address_line_2"] == "Westminster"
        assert breacher["country"] == "GB"

    @patch("report_a_suspected_breach.models.get_all_cleaned_data")
    @patch("report_a_suspected_breach.models.Breach.get_email_verification_object")
    @patch("report_a_suspected_breach.models.Breach.get_reporter_details")
    def test_supplier_save(
        self, patched_get_reporter_details, patched_get_email_verification, patched_cleaned_data, request_object
    ):
        session = request_object.session
        session["where_were_the_goods_supplied_from"] = {
            "where_were_the_goods_supplied_from": "different_uk_address",
        }
        session.save()

        patched_cleaned_data.return_value = self.basic_create_dict | {
            "about_the_supplier": {
                "name": "Test Supplier",
                "address_line_1": "Supplier Palace",
                "address_line_2": "Westminster",
                "country": "GB",
                "website": "https://www.supplier.com",
                "town_or_city": "London",
                "postal_code": "SW1A 1AA",
            }
        }

        patched_get_email_verification.return_value = ReporterEmailVerification.objects.create(
            email_verification_code="012345", verified=True
        )

        patched_get_reporter_details.return_value = {
            "full_name": "Chris",
            "name_of_business_you_work_for": "DBT",
            "email_address": "test@example.com",
            "professional_relationship": "owner",
        }

        breach = Breach.create_from_session(request_object)
        supplier = breach.personorcompany_set.get(type_of_relationship="supplier")
        assert supplier.name == "Test Supplier"
        assert supplier.address_line_1 == "Supplier Palace"
        assert supplier.address_line_2 == "Westminster"
        assert supplier.country == "GB"
        assert supplier.website == "https://www.supplier.com"

        session["where_were_the_goods_supplied_from"] = {
            "where_were_the_goods_supplied_from": "same_address",
        }
        session.save()
        # now we shouldn't see an additional supplier
        breach = Breach.create_from_session(request_object)
        assert breach.personorcompany_set.filter(type_of_relationship="supplier").count() == 0

    @patch("report_a_suspected_breach.models.get_all_cleaned_data")
    @patch("report_a_suspected_breach.models.Breach.get_email_verification_object")
    @patch("report_a_suspected_breach.models.Breach.get_reporter_details")
    def test_end_user_save(
        self, patched_get_reporter_details, patched_get_email_verification, patched_cleaned_data, request_object
    ):
        patched_cleaned_data.return_value = self.basic_create_dict | {
            "about_the_supplier": {
                "name": "Test Supplier",
                "address_line_1": "Supplier Palace",
                "address_line_2": "Westminster",
                "country": "GB",
                "website": "https://www.supplier.com",
                "town_or_city": "London",
                "postal_code": "SW1A 1AA",
            }
        }

        patched_get_email_verification.return_value = ReporterEmailVerification.objects.create(
            email_verification_code="012345", verified=True
        )

        patched_get_reporter_details.return_value = {
            "full_name": "Chris",
            "name_of_business_you_work_for": "DBT",
            "email_address": "test@example.com",
            "professional_relationship": "owner",
        }

        session = request_object.session
        session["end_users"] = {
            str(uuid.uuid4()): {
                "cleaned_data": {
                    "name_of_person": "Test End User",
                    "address_line_1": "End User Palace",
                    "address_line_2": "Westminster",
                    "country": "GB",
                    "website": "https://www.enduser.com",
                    "town_or_city": "London",
                    "postal_code": "SW1A 1AA",
                }
            },
            str(uuid.uuid4()): {
                "cleaned_data": {
                    "name_of_person": "Test End User 2",
                    "address_line_1": "End User Palace 2",
                    "address_line_2": "Westminster",
                    "country": "GB",
                    "website": "https://www.enduser2.com",
                    "town_or_city": "London",
                    "postal_code": "SW1A 1AA",
                }
            },
        }
        session.save()

        breach = Breach.create_from_session(request_object)
        end_users = breach.personorcompany_set.filter(type_of_relationship="recipient")
        assert end_users.count() == 2
        end_user_1 = end_users.get(name="Test End User")
        assert end_user_1.address_line_1 == "End User Palace"
        assert end_user_1.address_line_2 == "Westminster"
        assert end_user_1.country == "GB"
        assert end_user_1.website == "https://www.enduser.com"

        end_user_2 = end_users.get(name="Test End User 2")
        assert end_user_2.address_line_1 == "End User Palace 2"
        assert end_user_2.address_line_2 == "Westminster"
        assert end_user_2.country == "GB"
        assert end_user_2.website == "https://www.enduser2.com"
