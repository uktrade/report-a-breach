from django.urls import path

from . import views

app_name = "view_a_suspected_breach"

urlpatterns = [
    path("summary_reports", views.DefaultSummaryReportsView.as_view(), name="summary_reports"),
    path("sorted_summary_reports", views.SortedSummaryReportsView.as_view(), name="sorted_summary_reports"),
    path("view/<uuid:pk>/", views.ViewASuspectedBreachView.as_view(), name="breach_report"),
    path("user_admin/", views.ManageUsersView.as_view(), name="user_admin"),
]
