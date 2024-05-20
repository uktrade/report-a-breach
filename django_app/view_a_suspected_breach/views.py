from typing import Any

from core.document_storage import PermanentDocumentStorage
from core.sites import require_view_a_breach
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import Breach, PersonOrCompany
from utils.companies_house import get_formatted_address
from utils.s3 import get_breach_documents

from .mixins import ActiveUserRequiredMixin, StaffUserOnlyMixin


@method_decorator(require_view_a_breach(), name="dispatch")
class ViewABreachView(LoginRequiredMixin, ActiveUserRequiredMixin, TemplateView):
    template_name = "view_a_suspected_breach/landing.html"


@method_decorator(require_view_a_breach(), name="dispatch")
class ManageUsersView(StaffUserOnlyMixin, TemplateView):
    template_name = "view_a_suspected_breach/user_admin.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pending_users"] = User.objects.filter(is_active=False, is_staff=False)
        context["accepted_users"] = User.objects.filter(is_active=True)
        return context

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        if update_user := self.request.GET.get("accept_user", None):
            user_to_accept = User.objects.get(id=update_user)
            user_to_accept.is_active = True
            user_to_accept.save()
            return HttpResponseRedirect(reverse("view_a_suspected_breach:user_admin"))

        if delete_user := self.request.GET.get("delete_user", None):
            denied_user = User.objects.get(id=delete_user)
            denied_user.delete()
            return HttpResponseRedirect(reverse("view_a_suspected_breach:user_admin"))

        return super().get(request, **kwargs)


@method_decorator(require_view_a_breach(), name="dispatch")
class ViewASuspectedBreachView(DetailView):
    template_name = "view_a_suspected_breach/view_a_suspected_breach.html"

    def get_object(self) -> Breach:
        self.breach = get_object_or_404(Breach, id=self.kwargs["pk"])
        return self.breach

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Breach
        context["breach"] = self.breach

        # Breacher
        if breacher := PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.breacher
        ).first():
            if breacher.registered_company_number:
                breacher_address = breacher.registered_office_address
            else:
                breacher_address = get_formatted_address(model_to_dict(breacher))
            context["breacher"] = breacher
            context["breacher_address"] = breacher_address

        # Supplier
        if supplier := PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.supplier
        ).first():
            supplier_address = get_formatted_address(model_to_dict(supplier))
            context["supplier"] = supplier
            context["supplier_address"] = supplier_address

        elif self.breach.where_were_the_goods_supplied_from == "same_address":
            if breacher:
                context["supplier"] = breacher
                context["supplier_address"] = breacher_address

        # End Users (recipients)
        recipients = PersonOrCompany.objects.filter(
            breach_id=self.breach.id, type_of_relationship=TypeOfRelationshipChoices.recipient
        )
        context["recipients"] = recipients

        # Sanctions Regimes
        sanctions = self.breach.sanctions_regimes.all()
        context["sanctions"] = sanctions

        # Documents
        upload_documents = get_breach_documents(PermanentDocumentStorage(), str(self.breach.id))
        context["documents"] = upload_documents

        return context
