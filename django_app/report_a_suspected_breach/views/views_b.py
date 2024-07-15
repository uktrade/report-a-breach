from typing import Any

from core.views import BaseFormView
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from report_a_suspected_breach import forms


class AreYouReportingCompaniesHouseBusinessView(BaseFormView):
    form_class = forms.AreYouReportingABusinessOnCompaniesHouseForm

    def get_success_url(self) -> str:
        is_companies_house_business = self.form.cleaned_data.get("business_registered_on_companies_house") in (
            "yes",
            "do_not_know",
        )
        if is_companies_house_business:
            return reverse_lazy("report_a_suspected_breach:do_you_know_the_registered_company_number")
        return reverse_lazy("report_a_suspected_breach:where_is_the_address_of_the_business_or_person")


class DoYouKnowTheRegisteredCompanyNumberView(BaseFormView):
    form_class = forms.DoYouKnowTheRegisteredCompanyNumberForm

    def form_valid(self, form: forms.DoYouKnowTheRegisteredCompanyNumberForm) -> HttpResponse:
        self.form = form
        self.request.session["company_details"] = self.form.cleaned_data
        return super().form_valid(form)

    def get_success_url(self) -> str:
        has_companies_house_number = self.form.cleaned_data.get("do_you_know_the_registered_company_number") == "yes"
        if has_companies_house_number:
            if self.request.session.get("company_details_500", ""):
                return reverse_lazy("report_a_suspected_breach:manual_companies_house_input")
            else:
                return reverse_lazy("report_a_suspected_breach:check_company_details")
        return reverse_lazy("report_a_suspected_breach:where_is_the_address_of_the_business_or_person")


class ManualCompaniesHouseView(BaseFormView):
    form_class = forms.ManualCompaniesHouseInputForm
    success_url = reverse_lazy("report_a_suspected_breach:where_is_the_address_of_the_business_or_person")


class CheckCompanyDetailsView(BaseFormView):
    form_class = forms.SummaryForm
    template_name = "report_a_suspected_breach/form_steps/check_company_details.html"
    success_url = reverse_lazy(
        "report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "overview_of_the_suspected_breach"}
    )

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["company_details"] = self.request.session["company_details"]
        return context


class WhereIsTheAddressOfTheBusinessOrPersonView(BaseFormView):
    form_class = forms.WhereIsTheAddressOfTheBusinessOrPersonForm

    def get_success_url(self) -> str:
        is_uk_address = self.form.cleaned_data.get("where_is_the_address") == "in_the_uk"
        return reverse("report_a_suspected_breach:business_or_person_details", kwargs={"is_uk_address": is_uk_address})


class BusinessOrPersonDetailsView(BaseFormView):
    form_class = forms.BusinessOrPersonDetailsForm
    success_url = reverse_lazy(
        "report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "overview_of_the_suspected_breach"}
    )

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["is_uk_address"] = True if "True" in self.request.path else False
        return kwargs
