from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls import re_path

from .views import NameView
from .views import ProfessionalRelationshipView
from .views import ReportSubmissionCompleteView
from .views import StartView
from .views import SummaryView

urlpatterns = [
    path("", StartView.as_view(), name="home"),
    path(r"page_1", NameView.as_view(), name="page_1"),
    path(r"page_2", ProfessionalRelationshipView.as_view(), name="page_2"),
    path("summary/<uuid:pk>/", SummaryView.as_view(), name="summary"),
    path("confirmation/<uuid:pk>", ReportSubmissionCompleteView.as_view(), name="confirmation"),
]
