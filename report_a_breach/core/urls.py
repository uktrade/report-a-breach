from django.urls import path

from .views import EmailView
from .views import LandingView
from .views import NameView
from .views import ReportABreachStartView
from .views import ReportSubmissionCompleteView
from .views import SummaryView
from .views import VerifyView

urlpatterns = [
    path("landing", LandingView.as_view(), name="landing"),
    path(r"start/<uuid:pk>", ReportABreachStartView.as_view(), name="start"),
    path(r"email/<uuid:pk>", EmailView.as_view(), name="email"),
    path(r"verify/<uuid:pk>", VerifyView.as_view(), name="verify"),
    path(r"name/<uuid:pk>", NameView.as_view(), name="name"),
    path("summary/<uuid:pk>/", SummaryView.as_view(), name="summary"),
    path("confirmation/<uuid:pk>", ReportSubmissionCompleteView.as_view(), name="confirmation"),
]
