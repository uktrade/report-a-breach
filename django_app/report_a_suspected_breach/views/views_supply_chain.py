import uuid
from typing import Any

from core.base_views import BaseFormView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from report_a_suspected_breach.forms import forms_supply_chain as forms
from utils.address_formatter import get_formatted_address


class WhereWereTheGoodsSuppliedFromView(BaseFormView):
    form_class = forms.WhereWereTheGoodsSuppliedFromForm

    @property
    def redirect_after_post(self) -> bool:
        """If the user selects the same address or I do not know, we want to redirect back to summary"""
        if self.form.cleaned_data.get("where_were_the_goods_supplied_from") in ["same_address", "i_do_not_know"]:
            return True
        else:
            return False

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.session.get("company_details", {}).get("do_you_know_the_registered_company_number", "") == "yes":
            address_string = self.request.session["company_details"].get("readable_address")
        else:
            address_string = get_formatted_address(self.request.session["business_or_person_details"])

        kwargs["address_string"] = address_string
        return kwargs

    def get_success_url(self) -> str:
        self.request.session["made_available_journey"] = False
        success_paths = {
            "about_the_supplier": ["different_uk_address", "outside_the_uk"],
            "where_were_the_goods_supplied_to": ["same_address", "i_do_not_know"],
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

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["is_uk_address"] = True if self.kwargs["is_uk_address"] == "True" else False
        return kwargs

    def get_success_url(self) -> str:
        if not self.request.session.get("made_available_journey"):
            return reverse("report_a_suspected_breach:where_were_the_goods_supplied_to")
        return reverse("report_a_suspected_breach:where_were_the_goods_made_available_to")


class WhereWereTheGoodsSuppliedToView(BaseFormView):
    form_class = forms.WhereWereTheGoodsSuppliedToForm
    redirect_after_post = False

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        # restore the form data from the end_user_uuid, if it exists
        if self.request.method == "GET":
            if end_user_uuid := self.kwargs.get("end_user_uuid", None):
                if end_users_location_dict := self.request.session.get("end_users_location", {}).get(end_user_uuid, None):
                    kwargs["data"] = end_users_location_dict["dirty_data"]
                kwargs["end_user_uuid"] = end_user_uuid

        return kwargs

    def form_valid(self, form: forms.AboutTheEndUserForm) -> HttpResponse:
        end_users_location = self.request.session.get("end_users_location", {})
        # get the end_user_uuid if it exists, otherwise create it
        if end_user_uuid := self.request.GET.get("end_user_uuid", self.kwargs.get("end_user_uuid")):
            # used to display the correct location of the end_user_uuid
            end_users_location[end_user_uuid] = {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        self.request.session["end_users_location"] = end_users_location
        return super().form_valid(form)

    def get_success_url(self) -> str:
        form_data = self.form.cleaned_data.get("where_were_the_goods_supplied_to")
        if form_data == "i_do_not_know":
            return reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")
        is_uk_address = form_data == "in_the_uk"
        self.request.session["is_uk_address"] = is_uk_address
        end_user_uuid = self.kwargs.get("end_user_uuid", str(uuid.uuid4()))
        return reverse("report_a_suspected_breach:about_the_end_user", kwargs={"end_user_uuid": end_user_uuid})


class AboutTheEndUserView(BaseFormView):
    form_class = forms.AboutTheEndUserForm
    success_url = reverse_lazy("report_a_suspected_breach:end_user_added")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()

        kwargs["data"] = None
        kwargs["form_h1_header"] = "End-user 1 details"
        # restore the form data from the end_user_uuid, if it exists
        if self.request.method == "GET":
            if end_user_uuid := self.kwargs.get("end_user_uuid", None):
                if end_users := self.request.session.get("end_users", {}):
                    if end_users_dict := end_users.get(end_user_uuid, None):
                        kwargs["data"] = end_users_dict["dirty_data"]
                        kwargs["form_h1_header"] = f"End-user {list(end_users).index(end_user_uuid) + 1} details"
                    else:
                        kwargs["form_h1_header"] = f"End-user {len(end_users) + 1} details"

        kwargs["is_uk_address"] = self.request.session["is_uk_address"]
        return kwargs

    def form_valid(self, form: forms.AboutTheEndUserForm) -> HttpResponse:
        end_users = self.request.session.get("end_users", {})
        # get the end_user_uuid if it exists, otherwise create it
        if end_user_uuid := self.request.GET.get("end_user_uuid", self.kwargs.get("end_user_uuid", str(uuid.uuid4()))):
            # used to display the end_user_uuid data in end_users_added.html
            end_users[end_user_uuid] = {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        self.request.session["end_users"] = end_users
        return super().form_valid(form)


class EndUserAddedView(BaseFormView):
    form_class = forms.EndUserAddedForm
    template_name = "report_a_suspected_breach/form_steps/end_user_added.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["end_users"] = self.request.session["end_users"]
        context["is_made_available_journey"] = self.request.session.get("made_available_journey")
        return context

    def get_success_url(self) -> str:
        add_end_user = self.form.cleaned_data["do_you_want_to_add_another_end_user"]
        if add_end_user:
            add_end_user_str = "?add_another_end_user=yes"
            if self.request.session.get("made_available_journey"):
                return f"{reverse('report_a_suspected_breach:where_were_the_goods_made_available_to')}{add_end_user_str}"
            else:
                return f"{reverse('report_a_suspected_breach:where_were_the_goods_supplied_to')}{add_end_user_str}"

        else:
            return reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")


class DeleteEndUserView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        success_url = reverse_lazy("report_a_suspected_breach:end_user_added")
        if end_user_uuid := self.request.POST.get("end_user_uuid"):
            end_users = self.request.session.pop("end_users", None)
            end_users.pop(end_user_uuid, None)
            self.request.session["end_users"] = end_users
            if len(end_users) == 0:
                success_url = reverse_lazy("report_a_suspected_breach:zero_end_users")
            if redirect_to := self.request.POST.get("success_url"):
                success_url = reverse_lazy(f"report_a_suspected_breach:{redirect_to}")
        return redirect(success_url)


class ZeroEndUsersView(BaseFormView):
    form_class = forms.ZeroEndUsersForm

    def form_valid(self, form: forms.ZeroEndUsersForm) -> HttpResponse:
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        add_end_user = self.form.cleaned_data["do_you_want_to_add_an_end_user"]
        if add_end_user:
            add_end_user_str = "?add_another_end_user=yes"
            if self.request.session.get("made_available_journey"):
                return f"{reverse('report_a_suspected_breach:where_were_the_goods_made_available_to')}{add_end_user_str}"
            else:
                return f"{reverse('report_a_suspected_breach:where_were_the_goods_supplied_to')}{add_end_user_str}"

        else:
            return reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")


class WhereWereTheGoodsMadeAvailableFromView(BaseFormView):
    form_class = forms.WhereWereTheGoodsMadeAvailableForm

    @property
    def redirect_after_post(self) -> bool:
        """If the user selects the same address or I do not know, we want to redirect back to summary"""
        if self.form.cleaned_data.get("where_were_the_goods_made_available_from") in ["same_address", "i_do_not_know"]:
            return True
        else:
            return False

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if self.request.session.get("company_details", {}).get("do_you_know_the_registered_company_number", "") == "yes":
            kwargs["address_string"] = self.request.session["company_details"].get("readable_address")
        else:
            kwargs["address_string"] = get_formatted_address(self.request.session["business_or_person_details"])

        return kwargs

    def get_success_url(self) -> str:
        success_paths = {
            "about_the_supplier": ["different_uk_address", "outside_the_uk"],
            "where_were_the_goods_made_available_to": ["same_address", "i_do_not_know"],
        }
        form_data = self.form.cleaned_data.get("where_were_the_goods_made_available_from")
        for path, choices in success_paths.items():
            if form_data in choices:
                if path == "about_the_supplier":
                    is_uk_address = form_data == "different_uk_address"
                    return reverse(f"report_a_suspected_breach:{path}", kwargs={"is_uk_address": is_uk_address})
                return reverse(f"report_a_suspected_breach:{path}")

    def form_valid(self, form: forms.WhereWereTheGoodsMadeAvailableForm) -> HttpResponse:
        self.request.session["made_available_journey"] = True
        return super().form_valid(form)


class WhereWereTheGoodsMadeAvailableToView(BaseFormView):
    form_class = forms.WhereWereTheGoodsMadeAvailableToForm
    redirect_after_post = False

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        # restore the form data from the end_user_uuid, if it exists
        if self.request.method == "GET":
            if end_user_uuid := self.kwargs.get("end_user_uuid", None):
                if end_users_location_dict := self.request.session.get("end_users_location", {}).get(end_user_uuid, None):
                    kwargs["data"] = end_users_location_dict["dirty_data"]
                kwargs["end_user_uuid"] = end_user_uuid

        return kwargs

    def form_valid(self, form: forms.AboutTheEndUserForm) -> HttpResponse:
        end_users_location = self.request.session.get("end_users_location", {})
        # get the end_user_uuid if it exists, otherwise create it
        if end_user_uuid := self.request.GET.get("end_user_uuid", self.kwargs.get("end_user_uuid")):
            # used to display the correct location of the end_user_uuid
            end_users_location[end_user_uuid] = {
                "cleaned_data": form.cleaned_data,
                "dirty_data": form.data,
            }
        self.request.session["end_users_location"] = end_users_location
        return super().form_valid(form)

    def get_success_url(self) -> str:
        form_data = self.form.cleaned_data.get("where_were_the_goods_made_available_to")
        if form_data == "i_do_not_know":
            return reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")
        is_uk_address = form_data == "in_the_uk"
        self.request.session["is_uk_address"] = is_uk_address
        end_user_uuid = self.kwargs.get("end_user_uuid", None)
        if end_user_uuid is None:
            end_user_uuid = str(uuid.uuid4())
        return reverse("report_a_suspected_breach:about_the_end_user", kwargs={"end_user_uuid": end_user_uuid})


class WereThereOtherAddressesInTheSupplyChainView(BaseFormView):
    form_class = forms.WereThereOtherAddressesInTheSupplyChainForm
    success_url = reverse_lazy(
        "report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "sanctions_breach_details"}
    )
