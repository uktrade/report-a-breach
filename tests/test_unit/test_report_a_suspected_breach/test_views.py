import datetime
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import PersonOrCompany, ReporterEmailVerification
from report_a_suspected_breach.views import ReportABreachWizardView


class TestReportABreachWizardView:
    verify_code = "123456"

    @pytest.fixture(autouse=True)
    def reporter_email_verification_object(self, rasb_client):
        self.obj = ReporterEmailVerification.objects.create(
            reporter_session=rasb_client.session._get_session_from_db(),
            email_verification_code=self.verify_code,
        )
        request_object = RequestFactory()
        request_object.session = rasb_client.session._get_session_from_db()
        self.request_object = request_object

    def setup_view(self, view, request, *args, **kwargs):
        """
        Mimic ``as_view()``, but returns view instance.
        Use this function to get view instances on which you can run unit tests,
        by testing specific methods.
        """

        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    @patch("report_a_suspected_breach.views.ReportABreachWizardView.get_all_cleaned_data")
    @patch("report_a_suspected_breach.views.ReportABreachWizardView.store_documents_in_s3")
    def test_done(self, mocked_store_documents_in_s3, request_object, rasb_client):
        verify_code = "123456"
        view = ReportABreachWizardView()
        view.storage = MagicMock()
        view.steps = MagicMock()
        view.get_all_cleaned_data.return_value = {
            "start": {"reporter_professional_relationship": "third_party"},
            "email": {"reporter_email_address": "morgan.rees@digital.trade.gov.uk"},
            "verify": {"email_verification_code": verify_code},
            "name": {"reporter_full_name": "a", "reporter_name_of_business_you_work_for": "a"},
            "business_or_person_details": {
                "name": "Test",
                "website": "http://fdsa.com",
                "country": "GB",
                "address_line_1": "fdsa",
                "address_line_2": "",
                "town_or_city": "fdsa",
                "county": "",
                "postal_code": "NP8 8PD",
                "readable_address": "fdsa,\n fdsa,\n NP8 8PD,\n GB",
            },
            "are_you_reporting_a_business_on_companies_house": {"business_registered_on_companies_house": "no"},
            "do_you_know_the_registered_company_number": {"do_you_know_the_registered_company_number": "no"},
            "when_did_you_first_suspect": {
                "when_did_you_first_suspect": datetime.date(1994, 3, 12),
                "is_the_date_accurate": "approximate",
            },
            "which_sanctions_regime": {"which_sanctions_regime": ["The Oscars", "The Tonys", "don't know"]},
            "what_were_the_goods": {"what_were_the_goods": "sfda"},
            "where_were_the_goods_supplied_from": {"where_were_the_goods_supplied_from": "outside_the_uk"},
            "about_the_supplier": {
                "name": "fsda",
                "website": "http://fdas.com",
                "country": "AX",
                "address_line_1": "a",
                "address_line_2": "a",
                "address_line_3": "a",
                "address_line_4": "a",
                "town_or_city": "a",
                "readable_address": "a,\n a,\n a,\n AX",
            },
            "where_were_the_goods_supplied_to": {"where_were_the_goods_supplied_to": "outside_the_uk"},
            "were_there_other_addresses_in_the_supply_chain": {
                "were_there_other_addresses_in_the_supply_chain": "yes",
                "other_addresses_in_the_supply_chain": "sdfadfafasf",
            },
            "tell_us_about_the_suspected_breach": {"tell_us_about_the_suspected_breach": "sdfafad"},
        }
        form_list = ["start"]
        self.setup_view(view, rasb_client, request_object)
        view.done(form_list)

    def test_save_person_or_company_to_db(self, breach_object):
        person_or_company = {
            "name": "Test",
            "website": "http://fdsa.com",
            "country": "GB",
            "address_line_1": "fdsa",
            "address_line_2": "",
            "town_or_city": "fdsa",
            "county": "",
            "postal_code": "NP8 8PD",
            "readable_address": "fdsa,\n fdsa,\n NP8 8PD,\n GB",
        }
        relationship = TypeOfRelationshipChoices.supplier
        view = ReportABreachWizardView()
        view.save_person_or_company_to_db(breach_object, person_or_company, relationship)
        business_or_company_details = PersonOrCompany.objects.all()
        assert len(business_or_company_details) == 1
