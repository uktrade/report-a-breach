import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import FormView, TemplateView

from report_a_breach.base_classes.views import BaseWizardView
from report_a_breach.question_content import RELATIONSHIP
from report_a_breach.utils.notifier import send_email

from .forms import (
    AboutTheEndUserForm,
    AreYouReportingABusinessOnCompaniesHouseForm,
    BusinessOrPersonDetailsForm,
    DeclarationForm,
    DoYouKnowTheRegisteredCompanyNumberForm,
    EmailForm,
    EmailVerifyForm,
    EndUserAddedForm,
    NameForm,
    StartForm,
    SummaryForm,
    TellUsAboutTheSuspectedBreachForm,
    UploadDocumentsForm,
    WereThereOtherAddressesInTheSupplyChainForm,
    WhatWereTheGoodsForm,
    WhenDidYouFirstSuspectForm,
    WhereIsTheAddressOfTheBusinessOrPersonForm,
    WhereWereTheGoodsMadeAvailableForm,
    WhereWereTheGoodsSuppliedFromForm,
    WhereWereTheGoodsSuppliedToForm,
)
from .models import Breach, SanctionsRegime, SanctionsRegimeBreachThrough


class ReportABreachWizardView(BaseWizardView):
    form_list = [
        ("start", StartForm),
        ("email", EmailForm),
        ("verify", EmailVerifyForm),
        ("name", NameForm),
        (
            "are_you_reporting_a_business_on_companies_house",
            AreYouReportingABusinessOnCompaniesHouseForm,
        ),
        ("do_you_know_the_registered_company_number", DoYouKnowTheRegisteredCompanyNumberForm),
        ("check_company_details", SummaryForm),
        (
            "where_is_the_address_of_the_business_or_person",
            WhereIsTheAddressOfTheBusinessOrPersonForm,
        ),
        ("business_or_person_details", BusinessOrPersonDetailsForm),
        ("when_did_you_first_suspect", WhenDidYouFirstSuspectForm),
        ("what_were_the_goods", WhatWereTheGoodsForm),
        ("where_were_the_goods_supplied_from", WhereWereTheGoodsSuppliedFromForm),
        ("where_were_the_goods_made_available_from", WhereWereTheGoodsMadeAvailableForm),
        ("where_were_the_goods_supplied_to", WhereWereTheGoodsSuppliedToForm),
        ("about_the_supplier", BusinessOrPersonDetailsForm),
        ("about_the_end_user", AboutTheEndUserForm),
        ("end_user_added", EndUserAddedForm),
        ("were_there_other_addresses_in_the_supply_chain", WereThereOtherAddressesInTheSupplyChainForm),
        ("upload_documents", UploadDocumentsForm),
        ("tell_us_about_the_suspected_breach", TellUsAboutTheSuspectedBreachForm),
        ("summary", SummaryForm),
        ("declaration", DeclarationForm),
    ]

    template_names_lookup = {
        "summary": "form_steps/summary.html",
        "check_company_details": "form_steps/check_company_details.html",
        "end_user_added": "form_steps/end_user_added.html",
        "declaration": "form_steps/declaration.html",
    }
    template_name = "form_steps/generic_form_step.html"
    storage_name = "report_a_breach.session.SessionStorage"

    # todo - use AWS S3 for this
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "temporary_storage"))

    def get_summary_context_data(self, form, context):
        cleaned_data = self.get_all_cleaned_data()
        context["form_data"] = cleaned_data
        context["business_obtained_from_companies_house"] = (
            cleaned_data["do_you_know_the_registered_company_number"]["do_you_know_the_registered_company_number"] == "yes"
        )
        return context

    def get(self, request, *args, **kwargs):
        if request.resolver_match.url_name == "report_a_breach_about_the_end_user":
            # we are on a specific end-user step
            self.storage.current_step = "about_the_end_user"
            return super().get(request, *args, step="about_the_end_user", **kwargs)
        return super().get(request, *args, **kwargs)

    def get_step_url(self, step):
        if step == "about_the_end_user" and "end_user_uuid" in self.kwargs:
            return reverse(
                "report_a_breach_about_the_end_user",
                kwargs={"end_user_uuid": self.kwargs["end_user_uuid"]},
            )
        return super().get_step_url(step)

    def process_about_the_end_user_step(self, form):
        current_end_users = self.request.session.get("end_users", {})

        end_user_uuid = self.kwargs.get("end_user_uuid", str(uuid.uuid4()))
        # want to save both the cleaned data (for rendering to the user in the summary page) and the dirty data
        # (for re-instantiating the form in the case of a user wanting to change their input)
        current_end_users[end_user_uuid] = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["end_users"] = current_end_users
        self.request.session.modified = True
        return self.get_form_step_data(form)

    def render_next_step(self, form, **kwargs):
        if self.steps.current == "end_user_added" and form.cleaned_data["do_you_want_to_add_another_end_user"]:
            return redirect(self.get_step_url("about_the_end_user"))
        return super().render_next_step(form, **kwargs)

    def process_do_you_know_the_registered_company_number_step(self, form):
        self.request.session.pop("company_details", None)
        self.request.session.modified = True

        if form.cleaned_data.get("do_you_know_the_registered_company_number") == "yes":
            self.request.session["company_details"] = form.cleaned_data

        return self.get_form_step_data(form)

    def process_email_step(self, form):
        reporter_email_address = form.cleaned_data.get("reporter_email_address")
        verify_code = get_random_string(6, allowed_chars="0123456789")
        self.request.session["verify_code"] = verify_code
        print(verify_code)
        send_email(
            email=reporter_email_address,
            context={"verification_code": verify_code},
            template_id=settings.EMAIL_VERIFY_CODE_TEMPLATE_ID,
        )
        self.request.session.modified = True
        return self.get_form_step_data(form)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current
        # we are overriding this method, so we call self.form_list rather than self.get_form_list(). The latter will
        # apply the conditional logic to the form list, which we don't want to do here.
        form_class = self.form_list[step]
        # prepare the kwargs for the form instance.
        kwargs = self.get_form_kwargs(step)
        kwargs.update(
            {
                "data": data,
                "files": files,
                "prefix": self.get_form_prefix(step, form_class),
                "initial": self.get_form_initial(step),
            }
        )
        return form_class(**kwargs)

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        kwargs["request"] = self.request

        if step == "business_or_person_details":
            where_is_the_address = (self.get_cleaned_data_for_step("where_is_the_address_of_the_business_or_person") or {}).get(
                "where_is_the_address", ""
            )
            is_uk_address = where_is_the_address == "in_the_uk"
            kwargs["is_uk_address"] = is_uk_address

        if step == "about_the_supplier":
            where_were_the_goods_supplied_from = (self.get_cleaned_data_for_step("where_were_the_goods_supplied_from") or {}).get(
                "where_were_the_goods_supplied_from", ""
            )
            is_uk_address = where_were_the_goods_supplied_from == "different_uk_address"
            kwargs["is_uk_address"] = is_uk_address

        if step == "about_the_end_user":
            where_were_the_goods_supplied_to = (self.get_cleaned_data_for_step("where_were_the_goods_supplied_to") or {}).get(
                "where_were_the_goods_supplied_to", ""
            )
            is_uk_address = where_were_the_goods_supplied_to == "in_the_uk"
            kwargs["is_uk_address"] = is_uk_address

        if step in (
            "where_were_the_goods_supplied_from",
            "where_were_the_goods_made_available_from",
        ):
            # todo - get address dict from companies house form
            address_dict = self.get_cleaned_data_for_step("business_or_person_details") or {}
            kwargs["address_dict"] = address_dict

        return kwargs

    def done(self, form_list, **kwargs):
        all_cleaned_data = self.get_all_cleaned_data()
        sanctions_regime = SanctionsRegime.objects.get(short_name="The Russia")
        new_breach = Breach.objects.create(
            reporter_professional_relationship=all_cleaned_data["reporter_professional_relationship"],
            reporter_email_address=all_cleaned_data["reporter_email_address"],
            reporter_full_name=all_cleaned_data["reporter_full_name"],
            what_were_the_goods=all_cleaned_data["what_were_the_goods"],
        )

        # temporary, to be removed when the forms are integrated into the user journey
        new_breach.additional_information = "N/A"

        sanctions_breach = SanctionsRegimeBreachThrough.objects.create(breach=new_breach, sanctions_regime=sanctions_regime)
        sanctions_breach.save()
        new_breach.sanctions_regimes.add(sanctions_regime)
        new_breach.save()
        self.request.session.clear()
        reference_id = str(new_breach.id).split("-")[0].upper()

        # TODO: the confirmation page is not currently rendering, to be fixed in DST-259
        kwargs["reference_id"] = reference_id
        return render(self.request, "confirmation.html")


class SummaryView(FormView):
    """
    The summary page will display the information the reporter has provided,
    and give them a chance to change any of it.
    The data is saved to the database after the reporter submits.
    """

    template_name = "summary.html"
    form_class = SummaryForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get("breach_instance")
        context["email"] = data["reporter_email_address"]
        context["full_name"] = data["reporter_full_name"]
        # map the DB label to the question text
        choice_dict = dict(RELATIONSHIP["choices"])
        context["company_relationship"] = choice_dict.get(data["reporter_professional_relationship"])
        context["pk"] = data["id"]
        return context

    def get_success_url(self):
        return reverse(
            "confirmation",
            kwargs={"pk": self.request.session["breach_instance"]["id"]},
        )

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_instance")
        reference_id = reporter_data["id"].split("-")[0].upper()
        reporter_data["reporter_confirmation_id"] = reference_id
        self.instance = Breach(id=reporter_data["id"])
        self.instance.reporter_email_address = reporter_data["reporter_email_address"]
        self.instance.reporter_full_name = reporter_data["reporter_full_name"]
        self.instance.reporter_professional_relationship = reporter_data["reporter_professional_relationship"]
        # TODO: remove  N/A when the real form is implemented
        self.instance.additional_information = "N/A"
        self.instance.save()
        self.request.session["breach_instance"] = reporter_data
        return super().form_valid(form)


class ReportSubmissionCompleteView(TemplateView):
    """
    The final step in the reporting a breach application.
    This view will display the reporters reference number and information on the
    next steps in the process.
    """

    # Note: we are not currently sending the confirmation email specified in the template.
    template_name = "confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["application_reference_number"] = kwargs["reference_id"]
        return context
