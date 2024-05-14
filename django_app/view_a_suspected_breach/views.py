from core.document_storage import PermanentDocumentStorage
from core.sites import require_view_a_breach
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import Breach, PersonOrCompany
from utils.companies_house import get_formatted_address
from utils.s3 import get_breach_documents


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
        context = super().get_context_data(**kwargs)

        if breacher := PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.breacher
        ).first():
            breacher_address = get_formatted_address(model_to_dict(breacher))
            context["breacher"] = breacher
            context["breacher_address"] = breacher_address
            context["breacher_address"] = breacher_address

        supplier = PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.supplier
        ).first()
        recipients = PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.recipient
        )
        sanctions = self.breach.sanctions_regimes.all()
        supplier_address = get_formatted_address(model_to_dict(supplier))

        upload_documents = get_breach_documents(PermanentDocumentStorage(), str(self.breach.id))
        context["breach"] = self.breach
        context["sanctions"] = "sanctions"

        context["supplier"] = supplier
        context["supplier_address"] = supplier_address
        context["recipients"] = recipients
        context["sanctions"] = sanctions
        print(upload_documents)
        context["documents"] = upload_documents
        return context
