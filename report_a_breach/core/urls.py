from django.urls import path, re_path

from .views import LandingView, ReportABreachWizardView, ReportSubmissionCompleteView

report_a_breach_wizard = ReportABreachWizardView.as_view(
    url_name="report_a_breach_step", done_step_name="confirmation"
)

urlpatterns = [
    path("landing", LandingView.as_view(), name="landing"),
    path("confirmation", ReportSubmissionCompleteView.as_view(), name="confirmation"),
    path("report_a_breach", report_a_breach_wizard, name="report_a_breach"),
    re_path(r"report_a_breach/(?P<step>.+)/$", report_a_breach_wizard, name="report_a_breach_step"),
]
