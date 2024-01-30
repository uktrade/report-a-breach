import os

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import FormView
from django.views.generic import TemplateView

from report_a_breach.base_classes.views import BaseModelFormView
from report_a_breach.base_classes.views import BaseView
from report_a_breach.constants import BREADCRUMBS_START_PAGE
from report_a_breach.question_content import RELATIONSHIP
from report_a_breach.utils.notifier import send_mail

from .forms import EmailForm
from .forms import EmailVerifyForm
from .forms import NameForm
from .forms import StartForm
from .forms import SummaryForm
from .models import Breach

EMAIL_TEMPLATE_ID = os.getenv("GOVUK_NOTIFY_TEMPLATE_EMAIL_VERIFICATION")


class LandingView(TemplateView):
    """
    This view displays the landing page for the report a trade sanctions breach application.
    """

    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context


class ReportABreachStartView(BaseModelFormView):
    form_class = StartForm

    def __init__(self):
        super().__init__(success_path="email")


class EmailView(BaseModelFormView):
    """
    This view allows the reporter to submit their email address.
    An email is sent to the reporter with a 6 digit verification code tied to their session data.
    """

    form_class = EmailForm

    def __init__(self):
        super().__init__(success_path="verify")

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_instance")
        reporter_email_address = form.cleaned_data.get("reporter_email_address")
        # TODO: check if this needs an explicit ttl
        reporter_data["verify_code"] = get_random_string(6, allowed_chars="0123456789")
        self.request.session["breach_instance"] = reporter_data
        send_mail(
            email=reporter_email_address,
            context={"verification_code": reporter_data["verify_code"]},
            template_id=EMAIL_TEMPLATE_ID,
        )
        return super().form_valid(form)

    # users will need to continue to the verify page even if summary is the referrer as the new email must be verified
    def get_success_url(self):
        return reverse("verify", kwargs={"pk": self.request.session["breach_instance"]["id"]})


class VerifyView(BaseView):
    """
    A verification page. The reporter must submit the 6 digit verification code
    provided via email in order to continue.
    """

    form_class = EmailVerifyForm
    template_name = "form.html"

    def __init__(self):
        super().__init__()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_instance")
        user_submitted_code = form.cleaned_data.get("reporter_verify_email")
        if user_submitted_code == reporter_data["verify_code"]:
            return super().form_valid(form)
        raise ValidationError("Please enter the 6 digit code sent to the provided email address")

    def get_success_url(self):
        return reverse(
            "name",
            kwargs={"pk": self.request.session["breach_instance"]["id"]},
        )


class NameView(BaseModelFormView):
    form_class = NameForm

    def __init__(self):
        super().__init__(success_path="summary")


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
    This view will display the reporters reference number and information on the next steps in the process.
    """

    # Note: we are not currently sending the confirmation email specified in the template.
    template_name = "confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_data = self.request.session.get("breach_instance")
        context["application_reference_number"] = session_data["reporter_confirmation_id"]
        return context
