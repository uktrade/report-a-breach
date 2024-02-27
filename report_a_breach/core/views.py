from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import FormView, TemplateView

from report_a_breach.base_classes.views import BaseWizardView
from report_a_breach.question_content import RELATIONSHIP
from report_a_breach.utils.notifier import send_email

from .forms import (
    AreYouReportingABusinessOnCompaniesHouseForm,
    CheckCompanyDetailsForm,
    DoYouKnowTheRegisteredCompanyNumberForm,
    EmailForm,
    EmailVerifyForm,
    NameForm,
    StartForm,
    SummaryForm,
    WhatWereTheGoodsForm,
    WhichSanctionsRegimeForm,
)
from .models import Breach, SanctionsRegime, SanctionsRegimeBreachThrough


class ReportABreachWizardView(BaseWizardView):
    form_list = [
        ("start", StartForm),
        ("email", EmailForm),
        ("verify", EmailVerifyForm),
        ("name", NameForm),
        ("which_sanctions_regime", WhichSanctionsRegimeForm),
        ("what_were_the_goods", WhatWereTheGoodsForm),
        (
            "are_you_reporting_a_business_on_companies_house",
            AreYouReportingABusinessOnCompaniesHouseForm,
        ),
        ("do_you_know_the_registered_company_number", DoYouKnowTheRegisteredCompanyNumberForm),
        ("check_company_details", CheckCompanyDetailsForm),
        ("summary", SummaryForm),
    ]
    template_names_lookup = {
        "summary": "summary.html",
        "check_company_details": "form_steps/check_company_details.html",
    }
    template_name = "form_steps/generic_form_step.html"

    def render(self, form=None, **kwargs):
        if self.steps.current == "summary":
            print(self.steps.next)
        rendered_response = super().render(form, **kwargs)
        return rendered_response

    def get_summary_context_data(self, form, **kwargs):
        context = self.get_all_cleaned_data()
        choice_dict = dict(RELATIONSHIP["choices"])
        context["company_relationship"] = choice_dict.get(
            context["reporter_professional_relationship"]
        )
        return context

    def process_do_you_know_the_registered_company_number_step(self, form):
        self.request.session.pop("company_details", None)
        self.request.session.modified = True

        if form.cleaned_data.get("do_you_know_the_registered_company_number") == "yes":
            self.request.session["company_details"] = form.cleaned_data

        else:
            self.request.session["redirect"] = "summary"
            self.request.session.modified = True

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

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        kwargs["request"] = self.request
        return kwargs

    def done(self, form_list, **kwargs):
        all_cleaned_data = self.get_all_cleaned_data()
        new_breach = Breach.objects.create(
            reporter_professional_relationship=all_cleaned_data[
                "reporter_professional_relationship"
            ],
            reporter_email_address=all_cleaned_data["reporter_email_address"],
            reporter_full_name=all_cleaned_data["reporter_full_name"],
            what_were_the_goods=all_cleaned_data["what_were_the_goods"],
        )

        if declared_sanctions := all_cleaned_data["which_sanctions_regime"]:
            print(declared_sanctions)
            for sanction in declared_sanctions:
                sanctions_regime = SanctionsRegime.objects.get(full_name=sanction)
                sanctions_breach = SanctionsRegimeBreachThrough.objects.create(
                    breach=new_breach, sanctions_regime=sanctions_regime
                )
                sanctions_breach.save()
                new_breach.sanctions_regimes.add(sanctions_regime)

        # temporary, to be removed when the forms are integrated into the user journey
        new_breach.additional_information = "N/A"

        new_breach.save()
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
        context["company_relationship"] = choice_dict.get(
            data["reporter_professional_relationship"]
        )
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
        self.instance.reporter_professional_relationship = reporter_data[
            "reporter_professional_relationship"
        ]
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
