import logging

from core.base_views import BaseFormView
from core.forms import GenericForm
from core.utils import update_last_activity_session_timestamp
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from report_a_suspected_breach.form_step_conditions import (
    show_name_and_business_you_work_for_page,
)
from report_a_suspected_breach.forms import forms_start as forms
from utils.notifier import verify_email

logger = logging.getLogger(__name__)


class StartView(BaseFormView):
    form_class = forms.StartForm

    def dispatch(self, request, *args, **kwargs):
        # refresh the session expiry timestamp. This is the start of the session
        update_last_activity_session_timestamp(request)
        return super().dispatch(request, *args, **kwargs)

    # If the user changes this then they will continue the journey based off what they've changed
    @property
    def redirect_after_post(self):
        if self.form.cleaned_data["reporter_professional_relationship"] in ["owner", "acting"]:
            if self.changed_fields.get("reporter_professional_relationship") in ["third_party", "no_professional_relationship"]:
                return False
        if self.form.cleaned_data["reporter_professional_relationship"] in ["third_party", "no_professional_relationship"]:
            if self.changed_fields.get("reporter_professional_relationship") in ["owner", "acting"]:
                return False
        return True

    def get_success_url(self):
        if "reporter_email_address" in self.request.session:
            # Checking if the user has already provided their email, if so then they don't have to do it again
            if show_name_and_business_you_work_for_page(self.request):
                return reverse_lazy("report_a_suspected_breach:name_and_business_you_work_for")
            else:
                return reverse_lazy("report_a_suspected_breach:name")
        return reverse_lazy("report_a_suspected_breach:email")


class WhatIsYourEmailAddressView(BaseFormView):
    form_class = forms.EmailForm
    success_url = reverse_lazy("report_a_suspected_breach:verify_email")

    def form_valid(self, form: forms.EmailForm) -> HttpResponse:
        reporter_email_address = form.cleaned_data["reporter_email_address"]
        self.request.session["reporter_email_address"] = reporter_email_address
        verify_email(reporter_email_address, self.request)
        return super().form_valid(form)


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class EmailVerifyView(BaseFormView):
    form_class = forms.EmailVerifyForm

    def get_success_url(self) -> str:
        if show_name_and_business_you_work_for_page(self.request):
            return reverse_lazy("report_a_suspected_breach:name_and_business_you_work_for")
        else:
            return reverse_lazy("report_a_suspected_breach:name")

    def form_valid(self, form: forms.EmailVerifyForm) -> HttpResponse:
        reporter_email = form.cleaned_data["email"]
        self.request.session["reporter_email_address"] = reporter_email
        verify_email(reporter_email, self.request)
        return super().form_valid(form)

    def form_invalid(self, form: forms.EmailVerifyForm) -> HttpResponse:
        if form.has_error("email_verification_code", "expired"):
            # we need to send the code again
            reporter_email_address = self.request.session["reporter_email_address"]
            verify_email(reporter_email_address, self.request)
        return super().form_invalid(form)


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class RequestVerifyCodeView(BaseFormView):
    form_class = GenericForm
    template_name = "report_a_suspected_breach/form_steps/request_verify_code.html"
    success_url = reverse_lazy("report_a_suspected_breach:verify_email")

    def form_valid(self, form: GenericForm) -> HttpResponse:
        reporter_email_address = self.request.session["reporter_email_address"]
        if getattr(self.request, "limited", False):
            logger.warning(f"User has been rate-limited: {reporter_email_address}")
            return self.form_invalid(form)
        verify_email(reporter_email_address, self.request)
        return super().form_valid(form)


class NameAndBusinessYouWorkForView(BaseFormView):
    form_class = forms.NameAndBusinessYouWorkForForm
    success_url = reverse_lazy(
        "report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "about_the_person_or_business"}
    )


class YourNameView(BaseFormView):
    form_class = forms.NameForm
    success_url = reverse_lazy(
        "report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "about_the_person_or_business"}
    )
