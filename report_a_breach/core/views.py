import os

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import FormView
from django.views.generic import TemplateView

from report_a_breach.constants import BREADCRUMBS_START_PAGE
from report_a_breach.constants import SERVICE_HEADER
from report_a_breach.utils.notifier import send_mail

from .forms import EmailForm
from .forms import EmailVerifyForm
from .forms import HomeForm
from .forms import NameForm
from .forms import ProfessionalRelationshipForm
from .forms import SummaryForm
from .models import BreachDetails

EMAIL_TEMPLATE_ID = os.getenv("GOVUK_NOTIFY_TEMPLATE_EMAIL_VERIFICATION")


class HomeView(FormView):
    """
    This view displays the landing page for the report a trade sanctions breach application.
    """

    form_class = HomeForm
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        reporter_data["id"] = str(breach_details_instance.id)
        self.request.session["breach_details_instance"] = reporter_data
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "email", kwargs={"pk": self.request.session["breach_details_instance"]["id"]}
        )


class BaseFormView(FormView):
    """
    The parent class for most forms in the report a breach application.
    Reference the associated forms.py and form.html for formatting and content.
    """

    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context


class EmailView(BaseFormView):
    """
    This view allows the reporter to submit their email address.
    An email is sent to the reporter with a 6 digit verification code tied to their session data.
    """

    form_class = EmailForm

    def __init__(self):
        super().__init__()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["success_url"] = self.get_success_url()
        return context

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_details_instance")
        reporter_data["reporter_email_address"] = form.cleaned_data.get("field")
        # TODO: check if this needs an explicit ttl
        reporter_data["verify_code"] = get_random_string(6, allowed_chars="0123456789")
        self.request.session["breach_details_instance"] = reporter_data
        send_mail(
            email=reporter_data["reporter_email_address"],
            context={"verification_code": reporter_data["verify_code"]},
            template_id=EMAIL_TEMPLATE_ID,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "verify", kwargs={"pk": self.request.session["breach_details_instance"]["id"]}
        )


class VerifyView(BaseFormView):
    """
    A verification page. The reporter must submit the 6 digit verification code
    provided via email in order to continue.
    """

    form_class = EmailVerifyForm

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_details_instance")
        user_submitted_code = form.cleaned_data.get("field")
        if user_submitted_code == reporter_data["verify_code"]:
            return super().form_valid(form)
        raise ValidationError("Please enter the 6 digit code sent to the provided email address")

    def get_success_url(self):
        return reverse(
            "name",
            kwargs={"pk": self.request.session["breach_details_instance"]["id"]},
        )


class NameView(BaseFormView):
    form_class = NameForm

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_details_instance")
        reporter_data["reporter_full_name"] = form.cleaned_data.get("field")
        self.request.session["breach_details_instance"] = reporter_data
        print(reporter_data)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "professional_relationship",
            kwargs={"pk": self.request.session["breach_details_instance"]["id"]},
        )


class ProfessionalRelationshipView(BaseFormView):
    form_class = ProfessionalRelationshipForm
    template_name = "choices_form.html"

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_details_instance")
        reporter_data["reporter_professional_relationship"] = form.cleaned_data.get("field")
        self.request.session["breach_details_instance"] = reporter_data
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "summary", kwargs={"pk": self.request.session["breach_details_instance"]["id"]}
        )


class SummaryView(FormView):
    """
    The summary page will display the information the reporter has provided,
    and give them a chance to change any of it.
    The data is saved to the database after the reporter submits.
    """

    template_name = "summary.html"
    form_class = SummaryForm

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get("breach_details_instance")
        context["email"] = data["reporter_email_address"]
        context["full_name"] = data["reporter_full_name"]
        context["company_relationship"] = data["reporter_professional_relationship"]
        context["pk"] = data["id"]
        return context

    def get_success_url(self):
        return reverse(
            "confirmation",
            kwargs={"pk": self.request.session["breach_details_instance"]["id"]},
        )

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_details_instance")
        reference_id = reporter_data["id"].split("-")[0].upper()
        reporter_data["reporter_confirmation_id"] = reference_id
        self.instance = BreachDetails(id=reporter_data["id"])
        self.instance.reporter_email_address = reporter_data["reporter_email_address"]
        self.instance.reporter_full_name = reporter_data["reporter_full_name"]
        self.instance.reporter_professional_relationship = reporter_data[
            "reporter_professional_relationship"
        ]
        self.instance.save()
        self.request.session["breach_details_instance"] = reporter_data
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
        session_data = self.request.session.get("breach_details_instance")
        context["service_header"] = SERVICE_HEADER
        context["application_reference_number"] = session_data["reporter_confirmation_id"]
        return context
