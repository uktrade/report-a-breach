import uuid

from core.views import BaseFormView
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from report_a_suspected_breach import forms


class WhereWereTheGoodsSuppliedFromView(BaseFormView):
    form_class = forms.WhereWereTheGoodsSuppliedFromForm

    def get_success_url(self) -> str:
        success_paths = {
            "about_the_supplier": ["different_uk_address", "outside_the_uk"],
            "where_were_the_goods_supplied_to": ["same_address", "do_not_know"],
            "where_were_the_goods_made_available_from": ["they_have_not_been_supplied"],
        }
        form_data = self.form.cleaned_data.get("where_were_the_goods_supplied_from")
        for path, choices in success_paths.items():
            if form_data in choices:
                if path == "about_the_supplier":
                    is_uk_address = form_data == "different_uk_address"
                    return reverse(f"report_a_suspected_breach:{path}", kwargs={"is_uk_address": is_uk_address})
                return reverse(f"report_a_suspected_breach:{path}")


class AboutTheSupplierView(BaseFormView):
    form_class = forms.AboutTheSupplierForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["is_uk_address"] = True if self.kwargs["is_uk_address"] == "True" else False
        return kwargs

    def get_success_url(self) -> str:
        if not self.request.session.get("made_available_journey"):
            return reverse("report_a_suspected_breach:where_were_the_goods_supplied_to")
        return reverse("report_a_suspected_breach:where_were_the_goods_supplied_from")


class WhereWereTheGoodsSuppliedToView(BaseFormView):
    form_class = forms.WhereWereTheGoodsSuppliedToForm

    def get_success_url(self) -> str:
        form_data = self.form.cleaned_data.get("where_were_the_goods_supplied_to")
        if form_data == "do_not_know":
            return reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")
        is_uk_address = form_data == "in_the_uk"
        return reverse("report_a_suspected_breach:about_the_end_user", kwargs={"is_uk_address": is_uk_address})


class AboutTheEndUserView(BaseFormView):
    form_class = forms.AboutTheEndUserForm
    success_url = reverse_lazy("report_a_suspected_breach:end_user_added")

    def form_valid(self, form: forms.AboutTheEndUserForm) -> HttpResponse:
        if not self.request.session.get("end_users"):
            self.request.session["end_users"] = {}

        form_data = self.form.cleaned_data.get("about_the_end_user")
        end_user_uuid = str(uuid.uuid4())
        self.request.session["end_users"][end_user_uuid] = form_data
        return super().form_valid(form)


class EndUserAddedView(BaseFormView):
    form_class = forms.EndUserAddedForm

    def get_success_url(self) -> str:
        form_data = self.form.cleaned_data.get("do_you_want_to_add_another_end_user")
        if form_data == "yes":
            return reverse("report_a_suspected_breach:where_were_the_goods_supplied_to")
        return reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")


class WereThereOtherAddressesInTheSupplyChainView(BaseFormView):
    form_class = forms.WereThereOtherAddressesInTheSupplyChainForm
    success_url = reverse_lazy(
        "report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "sanctions_breach_details"}
    )


class WhereWereTheGoodsMadeAvailableFromView(BaseFormView):
    form_class = forms.WhereWereTheGoodsMadeAvailableFromForm

    def get_success_url(self) -> str:
        success_paths = {
            "about_the_supplier": ["different_uk_address", "outside_the_uk"],
            "where_were_the_goods_made_available_to": ["same_address", "do_not_know"],
        }
        form_data = self.form.cleaned_data.get("where_were_the_goods_made_available_from")
        for path, choices in success_paths.items():
            if form_data in choices:
                if path == "about_the_supplier":
                    is_uk_address = form_data == "different_uk_address"
                    return reverse(f"report_a_suspected_breach:{path}", kwargs={"is_uk_address": is_uk_address})
                return reverse(f"report_a_suspected_breach:{path}")

    def form_valid(self, form: forms.WhereWereTheGoodsMadeAvailableFromForm) -> HttpResponse:
        self.request.session["made_available_journey"] = True
        self.request.session.modified = True
        return super().form_valid(form)


class WhereWereTheGoodsMadeAvailableToView(BaseFormView):
    form_class = forms.WhereWereTheGoodsMadeAvailableToForm

    def get_success_url(self) -> str:
        form_data = self.form.cleaned_data.get("where_were_the_goods_made_available_to")
        if form_data == "do_not_know":
            return reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")
        is_uk_address = form_data == "in_the_uk"
        return reverse("report_a_suspected_breach:about_the_end_user", kwargs={"is_uk_address": is_uk_address})
