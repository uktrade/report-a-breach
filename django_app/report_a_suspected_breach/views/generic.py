from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, TemplateView


class RedirectBaseReportView(RedirectView):
    """Redirects report_a_breach base site visits to tasklist view"""

    @property
    def url(self) -> str:
        return reverse("report_a_suspected_breach:tasklist")


class TaskListView(TemplateView):
    template_name = "report_a_suspected_breach/tasklist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasklist = [
            {"title": "Your details", "key": "reporter_details", "url": reverse_lazy("report_a_suspected_breach:start")},
            {
                "title": "Name and business of the person or ",
                "key": "about_the_person_or_business",
                "help_text": "",
                "url": reverse_lazy("report_a_suspected_breach:are_you_reporting_a_business_on_companies_house"),
            },
            {
                "title": "Overview of the suspected breach",
                "key": "overview_of_the_suspected_breach",
                "help_text": "Which sanctions were breached, and what were the goods or services",
                "url": reverse_lazy("report_a_suspected_breach:when_did_you_first_suspect"),
            },
            {
                "title": "People and businesses involved",
                "key": "supply_chain",
                "help_text": "Contact details for the supplier, end-user and anyone else involved in the trade",
                "url": reverse_lazy("report_a_suspected_breach:where_were_the_goods_supplied_from"),
            },
            {
                "title": "Sanctions breach details",
                "key": "sanctions_breach_details",
                "help_text": "Upload documents and give any additional information",
                "url": reverse_lazy("report_a_suspected_breach:upload_documents"),
            },
            {
                "title": "Review and submit",
                "key": "review_and_submit",
                "help_text": "Check your answers before you submit your report",
                "url": reverse_lazy("report_a_suspected_breach:check_your_answers"),
            },
        ]

        current_task_name = kwargs.get("current_task_name", "reporter_details")

        seen_current_task = False
        for task in tasklist:
            if task["key"] == current_task_name:
                seen_current_task = True
                task["current_task"] = True
                task["can_start"] = True
                task["status_text"] = "Not yet started"
            elif seen_current_task:
                task["status_text"] = "Cannot start yet"
                task["can_start"] = False
            else:
                task["status_text"] = "Completed"
                task["can_start"] = False

        context["tasklist"] = tasklist

        return context
