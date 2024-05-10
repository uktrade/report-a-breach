from core.sites import require_view_a_breach
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import Breach, PersonOrCompany


@method_decorator(login_required, name="dispatch")
@method_decorator(require_view_a_breach(), name="dispatch")
class ViewABreachView(TemplateView):
    template_name = "view_a_suspected_breach/landing.html"


class ViewASuspectedBreachView(DetailView):
    template_name = "view_a_suspected_breach/view_a_suspected_breach.html"

    def get_queryset(self):
        self.breach = get_object_or_404(Breach, id=self.kwargs["pk"])
        return Breach.objects.filter(id=self.breach.id)

    def get_context_data(self, **kwargs):
        breacher = PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.breacher
        )
        supplier = PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.supplier
        )
        recipients = PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.recipient
        )

        print(breacher)
        print(supplier)
        print(recipients)
        context = super().get_context_data(**kwargs)
        context["breach"] = self.breach
        context["sanctions"] = "sanctions"
        context["breacher"] = breacher
        context["supplier"] = supplier
        context["recipients"] = recipients
        context["documents"] = ["documents"]
        return context
