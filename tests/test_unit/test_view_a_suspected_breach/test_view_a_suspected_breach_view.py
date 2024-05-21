from django.test import RequestFactory
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import (
    PersonOrCompany,
    SanctionsRegimeBreachThrough,
)
from view_a_suspected_breach.views import ViewASuspectedBreachView


class TestViewASuspectedBreachView:

    def test_get_object(self, vasb_client, breach_object):
        request_object = RequestFactory().get("/view/{pk}", kwargs={"pk": breach_object.id})
        view = ViewASuspectedBreachView()
        view.setup(request_object, pk=breach_object.id)
        breach = view.get_object()
        assert breach.id == breach_object.id

    def test_get_context_data(self, vasb_client, breach_with_sanctions_object):
        breach_id = breach_with_sanctions_object.id
        response = vasb_client.get(f"/view_a_suspected_breach/view/{breach_id}/")
        sanctions_regimes = SanctionsRegimeBreachThrough.objects.all()
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
        assert set(breach_with_sanctions_object.sanctions_regimes.through.objects.all()) == set(sanctions_regimes)

    def test_get_context_data_companies_house(self, vasb_client, breach_with_companies_house_object):
        breach_id = breach_with_companies_house_object.id
        response = vasb_client.get(f"/view_a_suspected_breach/{breach_id}/")
        sanctions_regimes = SanctionsRegimeBreachThrough.objects.all()
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
        assert set(breach_with_companies_house_object.sanctions_regimes.through.objects.all()) == set(sanctions_regimes)
