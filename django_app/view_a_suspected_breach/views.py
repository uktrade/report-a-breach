from typing import Any

from core.sites import require_view_a_breach
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, FormView, TemplateView
from report_a_suspected_breach.models import Breach
from utils.breach_report import get_breach_context_data

from .forms import SelectForm
from .mixins import ActiveUserRequiredMixin, StaffUserOnlyMixin

# ALL VIEWS HERE MUST BE DECORATED WITH AT LEAST LoginRequiredMixin


@method_decorator(require_view_a_breach(), name="dispatch")
class SummaryReportsView(LoginRequiredMixin, ActiveUserRequiredMixin, FormView):
    template_name = "view_a_suspected_breach/summary_reports.html"
    form_class = SelectForm
    success_url = reverse_lazy("view_a_suspected_breach:summary_reports")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        initial_dict = {}

        if sort := self.request.session.get("sort", ""):
            initial_dict["sort"] = sort
            kwargs["initial"] = initial_dict

        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        sort = self.request.session.pop("sort", "")
        # don't query again if the user hasn't selected a new sort and if the context data already exists
        if not sort and context.get("breach_objects", []):
            return context
        context["breach_objects"] = []
        breach_objects = Breach.objects.all()
        sorted_breaches = breach_objects.order_by("-created_at")
        if sort == "oldest":
            sorted_breaches = reversed(sorted_breaches)
        for breach in sorted_breaches:
            context["breach_objects"].extend([get_breach_context_data({}, breach)])
        return context

    def form_valid(self, form: SelectForm) -> HttpResponse:
        self.request.session["sort"] = form.cleaned_data["sort_by"]
        self.request.session.modified = True
        return super().form_valid(form)


@method_decorator(require_view_a_breach(), name="dispatch")
class ManageUsersView(LoginRequiredMixin, StaffUserOnlyMixin, TemplateView):
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
class ViewASuspectedBreachView(LoginRequiredMixin, ActiveUserRequiredMixin, DetailView):
    template_name = "view_a_suspected_breach/view_a_suspected_breach.html"

    def get_object(self, queryset=None) -> Breach:
        self.breach = get_object_or_404(Breach, id=self.kwargs["pk"])
        return self.breach

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return get_breach_context_data(context, self.breach)
