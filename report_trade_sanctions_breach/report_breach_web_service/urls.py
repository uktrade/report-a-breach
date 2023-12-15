from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views import View

from .views import (
    FirstFormView,
    StartView,
    ConfirmationView,
    SubmissionCompleteView
)

urlpatterns = [
    path("", StartView.as_view(), name="home"),
    path("page_1", FirstFormView.as_view()),
    path("confirmation/", ConfirmationView.as_view(), name="confirmation"),
    path("submission_complete/", SubmissionCompleteView.as_view(), name="submission_complete"),
    # path(r"assets/images", View.as_view()),
    # path(r"javascript/", View.as_view()),
    # path(r"stylesheets/", View.as_view())
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
