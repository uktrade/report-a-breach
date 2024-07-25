from typing import Any

from core.base_views import BaseFormView, BaseTemplateView
from core.document_storage import TemporaryDocumentStorage
from report_a_suspected_breach.form_step_conditions import (
    show_check_company_details_page_condition,
    show_name_and_business_you_work_for_page,
)
from report_a_suspected_breach.forms import DeclarationForm
from report_a_suspected_breach.utils import get_cleaned_data_for_step
from utils.s3 import get_all_session_files


class CheckYourAnswersView(BaseTemplateView):
    """View for the 'Check your answers' page."""

    template_name = "report_a_suspected_breach/form_steps/check_your_answers.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""
        from report_a_suspected_breach.urls import step_to_view_dict

        context = super().get_context_data(**kwargs)

        all_cleaned_data = {}
        form_views = [step for step, view in step_to_view_dict.items() if getattr(view, "form_class", None)]
        for step_name in form_views:
            all_cleaned_data[step_name] = get_cleaned_data_for_step(self.request, step_name)

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
