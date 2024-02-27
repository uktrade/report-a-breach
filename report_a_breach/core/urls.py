from django.urls import path, re_path

from .views import ReportABreachWizardView, ReportSubmissionCompleteView


def show_check_company_details_page_condition(wizard):
    cleaned_data = (
        wizard.get_cleaned_data_for_step("do_you_know_the_registered_company_number") or {}
    )
    return cleaned_data.get(
        "do_you_know_the_registered_company_number", False
    ) and cleaned_data.get("registered_company_number", False)


report_a_breach_wizard = ReportABreachWizardView.as_view(
    url_name="report_a_breach_step",
    done_step_name="confirmation",
    condition_dict={"check_company_details": show_check_company_details_page_condition},
)

urlpatterns = [
    path("confirmation", ReportSubmissionCompleteView.as_view(), name="confirmation"),
    path("", report_a_breach_wizard, name="report_a_breach"),
    re_path(r"report_a_breach/(?P<step>.+)/$", report_a_breach_wizard, name="report_a_breach_step"),
]
