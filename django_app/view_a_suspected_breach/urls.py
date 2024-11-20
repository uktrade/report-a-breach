from django.urls import path

from . import views

app_name = "view_a_suspected_breach"

urlpatterns = [
    path("", views.RedirectBaseViewerView.as_view(), name="initial_redirect_view"),
    path("view-all-reports", views.SummaryReportsView.as_view(), name="summary_reports"),
    path("view-report/<str:reference>/", views.ViewASuspectedBreachView.as_view(), name="breach_report"),
    path("manage-users/", views.ManageUsersView.as_view(), name="user_admin"),
    path("view-feedback/", views.ViewFeedbackView.as_view(), name="view_feedback"),
]
