import os
import uuid

from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import FormView
from django.views.generic import TemplateView
from dotenv import load_dotenv

from .constants import BREADCRUMBS_START_PAGE
from .constants import SERVICE_HEADER
from .forms import EmailForm
from .forms import EmailVerifyForm
from .forms import NameForm
from .forms import ProfessionalRelationshipForm
from .forms import StartForm
from .forms import SummaryForm
from .models import BreachDetails
from .notifier import send_mail

load_dotenv()
EMAIL_TEMPLATE_ID = os.getenv("GOVUK_NOTIFY_TEMPLATE_EMAIL_VERIFICATION")


class StartView(FormView):
    """
    This view displays the landing page for the report a trade sanctions breach application.
    """

    form_class = StartForm
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        reporter_data["report_id"] = str(breach_details_instance.report_id)
        # reporter_data["report_id"] = str(breach_details_instance.report_id)
        self.request.session["breach_details_instance"] = reporter_data
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "email", kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]}
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


class NameView(BaseFormView):
    form_class = NameForm
    # success_url = reverse_lazy("page_2")

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        reporter_data["reporter_full_name"] = breach_details_instance.reporter_full_name
        # reporter_data["report_id"] = str(breach_details_instance.report_id)
        self.request.session["breach_details_instance"] = reporter_data
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "professional_relationship",
            kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]},
        )


class EmailView(BaseFormView):
    form_class = EmailForm

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        reporter_data["reporter_email_address"] = breach_details_instance.reporter_email_address
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
            "verify", kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]}
        )


class VerifyView(BaseFormView):
    form_class = EmailVerifyForm

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        user_submitted_code = form.cleaned_data.get("reporter_verify_email")
        if user_submitted_code == reporter_data["verify_code"]:
            return super().form_valid(form)
        raise ValidationError("Please enter the 6 digit code sent to the provided email address")

    def get_success_url(self):
        return reverse(
            "name",
            kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]},
        )


class ProfessionalRelationshipView(BaseFormView):
    form_class = ProfessionalRelationshipForm

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        reporter_data[
            "reporter_professional_relationship"
        ] = breach_details_instance.reporter_professional_relationship
        # reporter_data["report_id"] = str(breach_details_instance.report_id)
        self.request.session["breach_details_instance"] = reporter_data
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "summary", kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]}
        )


class SummaryView(FormView):
    """
    The summary page will display the information the reporter has provided,
    and give them a chance to change any of it.
    The data is saved to the database after the reporter submits.
    """

    template_name = "summary.html"
    form_class = SummaryForm
    # model = BreachDetails

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get("breach_details_instance")
        context["email"] = data["reporter_email_address"]
        context["full_name"] = data["reporter_full_name"]
        context["company_relationship"] = data["reporter_professional_relationship"]
        context["success_url"] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse(
            "confirmation",
            kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]},
        )

    def form_valid(self, form):
        reporter_data = self.request.session.get("breach_details_instance")
        reference_id = reporter_data["report_id"].split("-")[0].upper()
        reporter_data["reporter_confirmation_id"] = reference_id
        self.instance = BreachDetails(report_id=reporter_data["report_id"])
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

    template_name = "confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_data = self.request.session.get("breach_details_instance")
        context["service_header"] = SERVICE_HEADER
        context["application_reference_number"] = session_data["reporter_confirmation_id"]
        return context
