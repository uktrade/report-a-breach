from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import NameView
from .views import ProfessionalRelationshipView
from .views import ReportSubmissionCompleteView
from .views import StartView

urlpatterns = [
    path("", StartView.as_view(), name="home"),
    path(r"page_1", NameView.as_view(), name="page_1"),
    path(r"page_2", ProfessionalRelationshipView.as_view(), name="page_2"),
    path(r"confirmation", ReportSubmissionCompleteView.as_view(), name="confirmation"),
    # path(r"assets/images", View.as_view()),
    # path(r"javascript/", View.as_view()),
    # path(r"stylesheets/", View.as_view())
    # TODO: the static urls can likely be removed
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
