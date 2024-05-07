from unittest.mock import MagicMock, patch

import pytest
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import (
    Breach,
    PersonOrCompany,
    ReporterEmailVerification,
    SanctionsRegime,
)
from report_a_suspected_breach.views import (
    ReportABreachWizardView,
    RequestVerifyCodeView,
)

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

    @patch("report_a_suspected_breach.form_step_conditions.show_about_the_supplier_page")
    @patch("report_a_suspected_breach.views.ReportABreachWizardView.store_documents_in_s3")
    @patch("report_a_suspected_breach.views.ReportABreachWizardView.get_all_cleaned_data")
    def test_done(
        self,
        mocked_get_all_cleaned_data,
        mocked_store_documents_in_s3,
        mocked_show_about_the_supplier_page,
        sanctions_regime_object,
        request_object,
        rasb_client,
    ):

        # Create Sanctions Regime Object
        sanctions_regime_name = SanctionsRegime.objects.all()[0].full_name
        data.cleaned_data["which_sanctions_regime"] = {"which_sanctions_regime": [sanctions_regime_name, "unknown_regime"]}

        # Setup Mock return values
        view = ReportABreachWizardView()
        view.storage = MagicMock()
        view.steps = MagicMock()
        mocked_get_all_cleaned_data.return_value = data.cleaned_data
        mocked_show_about_the_supplier_page.return_value = True

        # SetUp session values
        form_list = []
        request_object = RequestFactory().get("/")
        request_object.session = rasb_client.session
        session = rasb_client.session
        session["end_users"] = data.end_users
        session.save()

        # SetUp View
        view.setup(request_object)

        # Call done method of view
        response = view.done(form_list)

        # Assert only one breach object created
        breach = Breach.objects.all()
        assert len(breach) == 1

        breacher = PersonOrCompany.objects.filter(breach=breach[0], type_of_relationship=TypeOfRelationshipChoices.breacher)
        supplier = PersonOrCompany.objects.filter(breach=breach[0], type_of_relationship=TypeOfRelationshipChoices.supplier)
        end_user = PersonOrCompany.objects.filter(breach=breach[0], type_of_relationship=TypeOfRelationshipChoices.recipient)

        # Assert breacher, supplier and end_users objects created
        assert len(breacher) == 1
        assert len(supplier) == 1
        assert len(end_user) == 3

        # Assert breach object associated with breacher, supplier, end_users
        assert breacher[0].breach == breach[0]
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


class TestRequestVerifyCodeView:

    @patch("utils.notifier.send_email")
    def test_form_valid(self, send_email_mock, rasb_client):
        request_object = RequestFactory().get("/")

        request_object.session = rasb_client.session
        session = rasb_client.session
        reporter_email_address = "test@testmail.com"
        session["reporter_email_address"] = reporter_email_address
        session.save()
        view = RequestVerifyCodeView()
        view.setup(request_object)
        response = view.form_valid(request_object)
        email_verifications = ReporterEmailVerification.objects.all()
        assert len(email_verifications) == 1
        assert str(email_verifications[0].reporter_session) == request_object.session.session_key

        assert send_email_mock.call_count == 1

        # Assert returns redirect
        redirect = HttpResponseRedirect(
            status=302, content_type="text/html; charset=utf-8", redirect_to="/report_a_suspected_breach/verify/"
        )

        assert response.status_code == redirect.status_code
        assert response["content-type"] == redirect["content-type"]
        assert response.url == redirect.url
