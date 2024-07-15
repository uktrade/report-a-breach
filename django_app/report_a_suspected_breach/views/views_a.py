from core.views import BaseFormView
from django.urls import reverse_lazy
from report_a_suspected_breach import forms
from report_a_suspected_breach.form_step_conditions import (
    show_name_and_business_you_work_for_page,
)
from utils.notifier import verify_email


class StartView(BaseFormView):
    form_class = forms.StartForm
    success_url = reverse_lazy("report_a_suspected_breach:email")


class WhatIsYourEmailAddressView(BaseFormView):
    form_class = forms.EmailForm
    success_url = reverse_lazy("report_a_suspected_breach:verify_email")

    def form_valid(self, form):
        reporter_email_address = form.cleaned_data["reporter_email_address"]
        self.request.session["reporter_email_address"] = reporter_email_address
        verify_email(reporter_email_address, self.request)
        return super().form_valid(form)


class EmailVerifyView(BaseFormView):
    form_class = forms.EmailVerifyForm

    def get_success_url(self):
        if show_name_and_business_you_work_for_page(self.request):
            return reverse_lazy("report_a_suspected_breach:name_and_business_you_work_for")
        else:
            return reverse_lazy("report_a_suspected_breach:name")

    def form_valid(self, form):
        form.verification_object.verified = True
        form.verification_object.save()
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
