from django.urls import path

from .views import EmailView
from .views import NameView
from .views import ProfessionalRelationshipView
from .views import ReportSubmissionCompleteView
from .views import StartView
from .views import SummaryView
from .views import VerifyView

urlpatterns = [
    path("home", StartView.as_view(), name="home"),
    path(r"email/<uuid:pk>", EmailView.as_view(), name="email"),
    path(r"verify/<uuid:pk>", VerifyView.as_view(), name="verify"),
    path(r"name/<uuid:pk>", NameView.as_view(), name="name"),
    path(
        r"professional_relationship/<uuid:pk>",
        ProfessionalRelationshipView.as_view(),
        name="professional_relationship",
    ),
    path("summary/<uuid:pk>/", SummaryView.as_view(), name="summary"),
    path("confirmation/<uuid:pk>", ReportSubmissionCompleteView.as_view(), name="confirmation"),
]
