from django.urls import path

from report_a_breach.core.views import EmailView
from report_a_breach.core.views import LandingView
from report_a_breach.core.views import NameView
from report_a_breach.core.views import ReportABreachStartView
from report_a_breach.core.views import ReportSubmissionCompleteView
from report_a_breach.core.views import SummaryView
from report_a_breach.core.views import VerifyView

urlpatterns = [
    path("home", LandingView.as_view(), name="home"),
    path(r"email/<uuid:pk>", EmailView.as_view(), name="email"),
    path(r"verify/<uuid:pk>", VerifyView.as_view(), name="verify"),
    path(r"name/<uuid:pk>", NameView.as_view(), name="name"),
    # path(
    #     r"professional_relationship/<uuid:pk>",
    #     ProfessionalRelationshipView.as_view(),
    #     name="professional_relationship",
    # ),
    path("summary/<uuid:pk>/", SummaryView.as_view(), name="summary"),
    path("confirmation/<uuid:pk>", ReportSubmissionCompleteView.as_view(), name="confirmation"),
    path("report_a_breach", ReportABreachStartView.as_view(), name="report_a_breach"),
]
