from django.urls import path
from django.urls import re_path

from .views import LandingView
from .views import ReportABreachWizardView
from .views import ReportSubmissionCompleteView
from .views import SummaryView

report_a_breach_wizard = ReportABreachWizardView.as_view(
    url_name="report_a_breach_step", done_step_name="finished"
)

urlpatterns = [
    path("landing", LandingView.as_view(), name="landing"),
    path("summary/<uuid:pk>/", SummaryView.as_view(), name="summary"),
    path("confirmation/<uuid:pk>", ReportSubmissionCompleteView.as_view(), name="confirmation"),
    path("report_a_breach", report_a_breach_wizard, name="report_a_breach"),
    re_path(r"report_a_breach/(?P<step>.+)/$", report_a_breach_wizard, name="report_a_breach_step"),
]
