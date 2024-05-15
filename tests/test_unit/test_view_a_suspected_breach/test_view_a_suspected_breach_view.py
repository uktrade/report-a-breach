from django.test import RequestFactory
from report_a_suspected_breach.models import SanctionsRegimeBreachThrough
from view_a_suspected_breach.views import ViewASuspectedBreachView


class TestViewASuspectedBreachView:

    def test_get_queryset(self, vasb_client, breach_object):
        request_object = RequestFactory().get("/{pk}", kwargs={"pk": breach_object.id})
        view = ViewASuspectedBreachView()
        view.setup(request_object, pk=breach_object.id)
        breach_queryset = view.get_queryset()
        assert len(breach_queryset) == 1
        assert breach_queryset[0].id == breach_object.id

    def test_get_context_data(self, vasb_client, breach_with_sanctions_object):
        response = vasb_client.get(f"/view_a_suspected_breach/{breach_with_sanctions_object.id}/")
        sanctions_regimes = SanctionsRegimeBreachThrough.objects.all()
        assert response.context["breach"] == breach_with_sanctions_object
        assert set(breach_with_sanctions_object.sanctions_regimes.through.objects.all()) == set(sanctions_regimes)
