import os

from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import FormView
from django.views.generic import TemplateView

from report_a_breach.base_classes.views import BaseWizardView
from report_a_breach.constants import BREADCRUMBS_START_PAGE
from report_a_breach.question_content import RELATIONSHIP
from report_a_breach.utils.notifier import send_mail

from .forms import EmailForm
from .forms import EmailVerifyForm
from .forms import NameForm
from .forms import StartForm
from .forms import SummaryForm
from .models import Breach
from .models import SanctionsRegime
from .models import SanctionsRegimeBreachThrough

EMAIL_TEMPLATE_ID = os.getenv("GOVUK_NOTIFY_TEMPLATE_EMAIL_VERIFICATION")


class ReportABreachWizardView(BaseWizardView):
    form_list = [
        ("start", StartForm),
        ("email", EmailForm),
        ("verify", EmailVerifyForm),
        ("name", NameForm),
        ("summary", SummaryForm),
    ]
    template_name = "form_wizard_step.html"

    def get_summary_template_name(self):
        return "summary.html"

    def get_summary_context_data(self, form):
        context_dict = self.get_all_cleaned_data()
        return context_dict

    def process_email_step(self, form):
        reporter_email_address = form.cleaned_data.get("reporter_email_address")
        verify_code = get_random_string(6, allowed_chars="0123456789")
        self.request.session["verify_code"] = verify_code
        print(verify_code)
        send_mail(
            email=reporter_email_address,
            context={"verification_code": verify_code},
            template_id=EMAIL_TEMPLATE_ID,
        )
        self.request.session.modified = True
        return self.get_form_step_data(form)

    def process_summary_step(self, form):
        print("I'm here")
        print(form.errors)
        all_cleaned_data = self.get_all_cleaned_data()
        sanctions_regime = SanctionsRegime.objects.all(short_name="The Russia")
        new_breach = Breach.objects.create(
            reporter_professional_relationship=all_cleaned_data[
                "reporter_professional_relationship"
            ],
            reporter_email_address=all_cleaned_data["reporter_email_address"],
            reporter_full_name=all_cleaned_data["reporter_full_name"],
        )
        new_breach.sanctions_regimes = SanctionsRegimeBreachThrough.objects.create(
            breach=new_breach.id, sanctions_regime=sanctions_regime.id
        )
        new_breach.additional_information = "N/A"
        new_breach.save()
        return self.get_form_step_data(form)

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        kwargs["request"] = self.request
        return kwargs

    def done(self, form_list, **kwargs):
        # print(form_list)
        # all_cleaned_data = self.get_all_cleaned_data()
        # sanctions_regime = SanctionsRegime.objects.all(short_name="The Russia")
        # new_breach = Breach.objects.create(
        #     reporter_professional_relationship=all_cleaned_data[
        #         "reporter_professional_relationship"
        #     ],
        #     reporter_email_address=all_cleaned_data["reporter_email_address"],
        #     reporter_full_name=all_cleaned_data["reporter_full_name"],
        # )
        # new_breach.sanctions_regimes = SanctionsRegimeBreachThrough.objects.create(
        #     breach=new_breach.id, sanctions_regime=sanctions_regime.id
        # )
        # new_breach.additional_information = "N/A"
        # new_breach.save()
        return render(
            self.request,
            "done.html",
        )

    # def done(self, form_list, **kwargs):
    #     all_cleaned_data = self.get_all_cleaned_data()
    #     Breach.objects.create(
    #         reporter_professional_relationship=all_cleaned_data[
    #             "reporter_professional_relationship"
    #         ],
    #         reporter_email_address=all_cleaned_data["reporter_email_address"],
    #         reporter_full_name=all_cleaned_data["reporter_full_name"],
    #     )
    #     return render(
    #         self.request,
    #         "done.html",
    #     )


class LandingView(TemplateView):
    """
    This view displays the landing page for the report a trade sanctions breach application.
    """

    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context


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
        session_data = self.request.session.get("breach_instance")
        context["application_reference_number"] = session_data["reporter_confirmation_id"]
        return context
