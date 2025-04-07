from django.urls import reverse

from django_app.report_a_suspected_breach.views.generic import (
    RedirectBaseReportView,
    TaskListView,
)


class TestRedirectBaseReportView:
    def test_redirect_base_report_view_url(self):
        view = RedirectBaseReportView()
        expected_url = reverse("report_a_suspected_breach:tasklist")
        assert view.url == expected_url


class TestTaskListView:
    def test_task_list_in_context(self):
        view = TaskListView()
        context = view.get_context_data()
        assert "tasklist" in context
