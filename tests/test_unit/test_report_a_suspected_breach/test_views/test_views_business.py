from django.urls import reverse

from django_app.report_a_suspected_breach.views.views_business import (
    BusinessOrPersonDetailsView,
)


class TestAreYouReportingCompaniesHouseBusinessView:

    def test_success_url(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:are_you_reporting_a_business_on_companies_house"),
            data={"business_registered_on_companies_house": "yes"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:do_you_know_the_registered_company_number")

        # if the business is not registered on companies house
        response = rasb_client.post(
            reverse("report_a_suspected_breach:are_you_reporting_a_business_on_companies_house"),
            data={"business_registered_on_companies_house": "no"},
        )

        assert response.url == reverse("report_a_suspected_breach:where_is_the_address_of_the_business_or_person")


class TestDoYouKnowTheRegisteredCompanyNumberView:

    def test_success_url(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:do_you_know_the_registered_company_number"),
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
        )

        assert response.status_code in [302, 200]
        assert response.url == reverse("report_a_suspected_breach:check_company_details")

        # when the user does not know the company_number
        response = rasb_client.post(
            reverse("report_a_suspected_breach:do_you_know_the_registered_company_number"),
            data={"do_you_know_the_registered_company_number": "no"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:where_is_the_address_of_the_business_or_person")


class TestWhereIsTheAddressOfTheBusinessOrPersonView:
    def test_success_url(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_is_the_address_of_the_business_or_person"),
            data={"where_is_the_address": "in_the_uk"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:business_or_person_details", kwargs={"is_uk_address": "True"})


class TestBusinessOrPersonDetailsView:
    def test_get_form_kwargs_uk_address(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session.save()
        view = BusinessOrPersonDetailsView()
        view.setup(request_object, is_uk_address="True")
        response = view.get_form_kwargs()
        assert response["is_uk_address"] is True

    def test_get_form_kwargs_non_uk_address(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session.save()
        view = BusinessOrPersonDetailsView()
        view.setup(request_object, is_uk_address=False)
        response = view.get_form_kwargs()
        assert response["is_uk_address"] is False
