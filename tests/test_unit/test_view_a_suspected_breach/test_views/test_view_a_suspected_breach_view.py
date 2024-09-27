from unittest.mock import patch

from core.sites import SiteName
from django.contrib.auth.models import User
from django.test import RequestFactory
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import PersonOrCompany
from view_a_suspected_breach.views import ViewASuspectedBreachView


class TestViewASuspectedBreachView:

    def test_get_object(self, vasb_client, breach_object):
        request_object = RequestFactory().get("/view/{pk}", kwargs={"pk": breach_object.id})
        view = ViewASuspectedBreachView()
        view.setup(request_object, pk=breach_object.id)
        breach = view.get_object()
        assert breach.id == breach_object.id

    @patch("view_a_suspected_breach.mixins.send_email")
    def test_get_context_data(self, mock_email, vasb_client, breach_with_sanctions_object):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )

        request_object = RequestFactory().get("/")
        request_object.user = test_user
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach

        vasb_client.force_login(test_user)

        breach_id = breach_with_sanctions_object.id
        response = vasb_client.get(f"/view_a_suspected_breach/view-report/{breach_id}/")
        breacher = PersonOrCompany.objects.filter(
            breach=breach_id, type_of_relationship=TypeOfRelationshipChoices.breacher
        ).first()
        supplier = PersonOrCompany.objects.filter(
            breach=breach_id, type_of_relationship=TypeOfRelationshipChoices.supplier
        ).first()
        recipients = PersonOrCompany.objects.filter(breach=breach_id, type_of_relationship=TypeOfRelationshipChoices.recipient)
        assert response.context["breach"] == breach_with_sanctions_object
        assert response.context["breacher"] == breacher
        assert response.context["supplier"] == supplier
        assert set(response.context["recipients"]) == set(recipients)

    @patch("view_a_suspected_breach.mixins.send_email")
    def test_get_context_data_companies_house(self, mock_email, vasb_client, breach_with_companies_house_object):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )

        request_object = RequestFactory().get("/")
        request_object.user = test_user
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach

        vasb_client.force_login(test_user)
        breach_id = breach_with_companies_house_object.id
        response = vasb_client.get(f"/view_a_suspected_breach/view-report/{breach_id}/")
        breacher = PersonOrCompany.objects.filter(
            breach=breach_id, type_of_relationship=TypeOfRelationshipChoices.breacher
        ).first()
        recipients = PersonOrCompany.objects.filter(breach=breach_id, type_of_relationship=TypeOfRelationshipChoices.recipient)
        assert response.context["breach"] == breach_with_companies_house_object
        assert response.context["breacher"] == breacher
        if breach_with_companies_house_object.where_were_the_goods_supplied_from == "same_address":
            assert response.context["supplier"].name == breacher.name
        else:
            assert "supplier" not in response.context.keys()
        assert set(response.context["recipients"]) == set(recipients)

    @patch("view_a_suspected_breach.mixins.send_email")
    def test_get_context_data_breacher_and_supplier(self, mock_email, vasb_client, breacher_and_supplier_object):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )

        request_object = RequestFactory().get("/")
        request_object.user = test_user
        request_object.site = SiteName
        request_object.site.name = SiteName.view_a_suspected_breach

        vasb_client.force_login(test_user)

        breach_id = breacher_and_supplier_object.id
        response = vasb_client.get(f"/view_a_suspected_breach/view-report/{breach_id}/")
        breacher = PersonOrCompany.objects.filter(
            breach=breach_id, type_of_relationship=TypeOfRelationshipChoices.breacher
        ).first()
        recipients = PersonOrCompany.objects.filter(breach=breach_id, type_of_relationship=TypeOfRelationshipChoices.recipient)
        assert response.context["breach"] == breacher_and_supplier_object
        assert response.context["breacher"] == breacher
        assert response.context["supplier"].name == breacher.name
        assert set(response.context["recipients"]) == set(recipients)
