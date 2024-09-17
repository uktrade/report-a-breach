from typing import Any

from core.base_views import BaseFormView, BaseTemplateView
from core.document_storage import TemporaryDocumentStorage
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.urls import reverse, reverse_lazy
from report_a_suspected_breach.form_step_conditions import (
    show_check_company_details_page_condition,
    show_name_and_business_you_work_for_page,
)
from report_a_suspected_breach.forms.forms_f import DeclarationForm
from report_a_suspected_breach.models import Breach
from report_a_suspected_breach.utils import (
    get_all_cleaned_data,
    get_cleaned_data_for_step,
)
from utils.breach_report import get_breach_context_data
from utils.notifier import send_email
from utils.s3 import get_all_session_files

from django_app.view_a_suspected_breach.utils import craft_view_a_suspected_breach_url


class CheckYourAnswersView(BaseTemplateView):
    """View for the 'Check your answers' page."""

    template_name = "report_a_suspected_breach/form_steps/check_your_answers.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""

        context = super().get_context_data(**kwargs)

        all_cleaned_data = get_all_cleaned_data(self.request)

        context["form_data"] = all_cleaned_data
        context["is_company_obtained_from_companies_house"] = show_check_company_details_page_condition(self.request)
        context["is_third_party_relationship"] = show_name_and_business_you_work_for_page(self.request)
        context["is_made_available_journey"] = self.request.session.get("made_available_journey")
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            context["form_data"]["session_files"] = session_files
        if end_users := self.request.session.get("end_users", None):
            context["form_data"]["end_users"] = end_users
        if (
            get_cleaned_data_for_step(self.request, "where_were_the_goods_supplied_from").get(
                "where_were_the_goods_supplied_from"
            )
            == "same_address"
            or get_cleaned_data_for_step(self.request, "where_were_the_goods_made_available_from").get(
                "where_were_the_goods_made_available_from"
            )
            == "same_address"
        ):
            if show_check_company_details_page_condition(self.request):
                registered_company = context["form_data"]["do_you_know_the_registered_company_number"]
                context["form_data"]["about_the_supplier"] = {}
                context["form_data"]["about_the_supplier"]["name"] = registered_company["registered_company_name"]
                context["form_data"]["about_the_supplier"]["readable_address"] = registered_company["registered_office_address"]
                context["form_data"]["about_the_supplier"]["country"] = "GB"
            else:
                context["form_data"]["about_the_supplier"] = context["form_data"]["business_or_person_details"]
        return context


class DeclarationView(BaseFormView):
    form_class = DeclarationForm
    template_name = "report_a_suspected_breach/form_steps/declaration.html"
    success_url = reverse_lazy("report_a_suspected_breach:complete")

    def form_valid(self, form):
        new_breach_object = Breach.create_from_session(self.request)
        # Send confirmation email to the user
        send_email(
            email=new_breach_object.reporter_email_address,
            template_id=settings.EMAIL_USER_REPORT_CONFIRMATION_TEMPLATE_ID,
            context={"user name": new_breach_object.reporter_full_name, "reference number": new_breach_object.reference},
        )
        # Send confirmation email to OTSI staff
        view_application_url = craft_view_a_suspected_breach_url(
            reverse("view_a_suspected_breach:breach_report", kwargs={"pk": new_breach_object.pk})
        )
        for user in User.objects.filter(is_staff=True):
            send_email(
                email=user.email,
                template_id=settings.OTSI_NEW_APPLICATION_TEMPLATE_ID,
                context={"application_number": new_breach_object.reference, "url": view_application_url},
            )
        self.request.session["breach_id"] = str(new_breach_object.pk)
        return super().form_valid(form)


class CompleteView(BaseTemplateView):
    template_name = "report_a_suspected_breach/form_steps/complete.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        breach_object = Breach.objects.get(pk=self.request.session.get("breach_id"))

        # we want to make sure that the user has access to the breach object,
        # so we check if the session that created the breach object is the same as the current session
        # if not, we raise a SuspiciousOperation. Sessions are wiped from the DB but users should really only see this
        # page once they have submitted a report, so this should not be an issue.
        if breach_object.reporter_session != self.request.session._get_session_from_db():
            raise SuspiciousOperation("User does not have access to this breach object.")

        context.update(get_breach_context_data(breach_object))
        return context
