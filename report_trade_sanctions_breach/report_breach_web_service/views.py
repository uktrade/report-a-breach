import os
from crispy_forms_gds.layout import HTML
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic import TemplateView

from .constants import BREADCRUMBS_START_PAGE
from .constants import SERVICE_HEADER

from .forms import (
    StartForm,
    ConfirmationForm
)

from .notifier import send_mail


class StartView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context


class FirstFormView(FormView):
    template_name = "form.html"
    form_class = StartForm
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context

class ConfirmationView(FormView):
    template_name = "confirmation.html"
    form_class = ConfirmationForm
    # success_url = reverse_lazy("submission_complete")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context
         
    def post(self, request, *args, **kwargs):

        email = os.environ["TEST_EMAIL"]
        context = {
            "email_address": email,
            "name": "Some Name",
            "verification_link": "www.bbc.com"
        }
        template_id = os.environ["GOVUK_NOTIFY_TEMPLATE_SANCTIONS_NOTIFY_CONFIRMATION_EMAIL"]
        
        # context, template_id, reference=None

        report = send_mail(email, context, template_id)

        return redirect(
            # reverse("invite_representative_sent", kwargs={"reference_number": self.reference_number["id"]})
            # reverse("submission_complete", kwargs={"reference_number": "F4K3NUM8"})
            reverse("submission_complete")
        )
   

class SubmissionCompleteView(TemplateView):
    template_name = "submission_complete.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["service_header"] = SERVICE_HEADER
    #     return context
