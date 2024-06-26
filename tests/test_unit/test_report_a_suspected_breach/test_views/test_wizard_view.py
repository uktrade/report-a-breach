import datetime as dt
from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import (
    Breach,
    PersonOrCompany,
    ReporterEmailVerification,
    SanctionsRegime,
)
from report_a_suspected_breach.views import ReportABreachWizardView

from . import data


class TestReportABreachWizardView:

    @pytest.fixture(autouse=True)
    def reporter_email_verification_object(self, rasb_client):
        self.obj = ReporterEmailVerification.objects.create(
            reporter_session=rasb_client.session._get_session_from_db(),
            email_verification_code=data.verify_code,
        )
        request_object = RequestFactory().get("/")
        self.request_object = request_object

    @pytest.mark.parametrize("cleaned_data_return", [data.cleaned_data, data.cleaned_companies_house_data])
    @patch("report_a_suspected_breach.form_step_conditions.show_about_the_supplier_page")
    @patch("report_a_suspected_breach.form_step_conditions.show_check_company_details_page_condition")
    @patch("report_a_suspected_breach.views.ReportABreachWizardView.store_documents_in_s3")
    @patch("report_a_suspected_breach.views.ReportABreachWizardView.get_all_cleaned_data")
    @patch("report_a_suspected_breach.views.send_email")
    def test_done(
        self,
        mock_send_email,
        mocked_get_all_cleaned_data,
        mocked_store_documents_in_s3,
        mocked_show_check_company_details_page_condition,
        mocked_show_about_the_supplier_page,
        cleaned_data_return,
        sanctions_regime_object,
        request_object,
        rasb_client,
    ):

        # Create Sanctions Regime Object
        sanctions_regime_name = SanctionsRegime.objects.all()[0].full_name
        data.cleaned_data["which_sanctions_regime"] = {"which_sanctions_regime": [sanctions_regime_name, "Unknown Regime"]}
        # Setup Mock return values
        view = ReportABreachWizardView()
        view.storage = MagicMock()
        view.steps = MagicMock()
        mocked_get_all_cleaned_data.return_value = cleaned_data_return
        mocked_show_about_the_supplier_page.return_value = True
        if cleaned_data_return["do_you_know_the_registered_company_number"]["do_you_know_the_registered_company_number"] == "yes":
            mocked_show_check_company_details_page_condition.return_value = True
        else:
            mocked_show_check_company_details_page_condition.return_value = False
        cleaned_data_return["which_sanctions_regime"] = {"which_sanctions_regime": [sanctions_regime_name, "Unknown Regime"]}

        # SetUp session values
        form_list = []
        request_object = RequestFactory().get("/")
        request_object.session = rasb_client.session
        session = rasb_client.session
        session["end_users"] = data.end_users
        session.save()

        # setup email verification object
        ReporterEmailVerification.objects.create(
            reporter_session=rasb_client.session._get_session_from_db(),
            email_verification_code="12345",
            date_created=dt.datetime.now(),
            verified=True,
        )

        # SetUp View
        view.setup(request_object)

        # Call done method of view
        response = view.done(form_list)

        assert mock_send_email.call_count == 1

        # Assert only one breach object created
        breach = Breach.objects.all()
        assert len(breach) == 1

        breacher = PersonOrCompany.objects.filter(breach=breach[0], type_of_relationship=TypeOfRelationshipChoices.breacher)
        supplier = PersonOrCompany.objects.filter(breach=breach[0], type_of_relationship=TypeOfRelationshipChoices.supplier)
        end_user = PersonOrCompany.objects.filter(breach=breach[0], type_of_relationship=TypeOfRelationshipChoices.recipient)
        # Assert breacher, supplier and end_users objects created

        assert len(breacher) == 1
        assert breacher[0].breach == breach[0]

        assert len(supplier) == 1
        assert len(end_user) == 3

        # Assert breach object associated with breacher, supplier, end_users
        assert supplier[0].breach == breach[0]
        assert end_user[1].breach == breach[0]

        # Assert Sanctions Regimes set
        assert breach[0].unknown_sanctions_regime is True
        assert breach[0].other_sanctions_regime is False
        assert breach[0].sanctions_regimes.all()[0].full_name == sanctions_regime_name

        # Assert returns redirect
        redirect = HttpResponseRedirect(
            status=302, content_type="text/html; charset=utf-8", redirect_to="/report_a_suspected_breach/complete"
        )

        assert response.status_code == redirect.status_code
        assert response["content-type"] == redirect["content-type"]
        assert response.url == redirect.url

    def test_save_person_or_company_to_db(self, breach_object):
        person_or_company = data.person_or_company
        relationship = TypeOfRelationshipChoices.supplier
        view = ReportABreachWizardView()
        view.save_person_or_company_to_db(breach_object, person_or_company, relationship)
        person_or_company_details = PersonOrCompany.objects.all()
        assert len(person_or_company_details) == 1
        assert person_or_company_details[0].type_of_relationship == relationship

    def test_where_were_the_goods_supplied_to_url(self, rasb_client):
        request = RequestFactory().get("/")
        request.session = rasb_client.session
        request.session["end_users"] = data.end_users
        end_user_id = "end_user1"
        request.session.save()

        response = rasb_client.get(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_to", args={"end_user_uuid": end_user_id}),
        )
        assert response.status_code == 200

    def test_where_were_the_goods_made_available_to_url(self, rasb_client):
        request = RequestFactory().get("/")
        request.session = rasb_client.session
        request.session["end_users"] = data.end_users
        end_user_id = "end_user3"

        response = rasb_client.get(
            reverse("report_a_suspected_breach:where_were_the_goods_made_available_to", args={"end_user_uuid": end_user_id}),
        )
        assert response.status_code == 200
