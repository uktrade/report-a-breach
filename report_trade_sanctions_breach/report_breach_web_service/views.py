import uuid

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import TemplateView

from .constants import BREADCRUMBS_START_PAGE
from .constants import SERVICE_HEADER
from .forms import NameForm
from .forms import ProfessionalRelationshipForm
from .models import BreachDetails


class StartView(TemplateView):
    """
    This view displays the landing page for the report a trade sanctions breach application.
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context


class BaseFormView(FormView):
    """
    The parent class for all forms in the report a breach application.
    Reference the associated forms.py and form.html for formatting and content.
    """

    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context


class NameView(BaseFormView):
    form_class = NameForm
    success_url = reverse_lazy("page_2")

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        reporter_data["reporter_full_name"] = breach_details_instance.reporter_full_name
        self.request.session["breach_details_instance"] = reporter_data
        return super().form_valid(form)


class ProfessionalRelationshipView(BaseFormView):
    form_class = ProfessionalRelationshipForm

    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        breach_details_instance = form.save(commit=False)
        reporter_data = self.request.session.get("breach_details_instance", {})
        reporter_data[
            "reporter_professional_relationship"
        ] = breach_details_instance.reporter_professional_relationship
        reporter_data["report_id"] = str(breach_details_instance.report_id)
        self.request.session["breach_details_instance"] = reporter_data
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "summary", kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]}
        )


# The app makes it as far as this view then can't find breach details.
# TODO: need to debug to find out why this view won't render
class SummaryView(TemplateView):
    """
    The summary page will display the information the reporter has provided,
    and give them a chance to change any of it.
    The data is saved to the database after the reporter submits.
    """

    template_name = "summary.html"
    model = BreachDetails

    def __init__(self):
        super().__init__()

    def get(self, request, *args, **kwargs):
        kwargs = self.kwargs
        self.object = self.request.session["breach_details_instance"]
        kwargs["reporter_full_name"] = self.object["reporter_full_name"]
        kwargs["reporter_professional_relationship"] = self.object[
            "reporter_professional_relationship"
        ]
        kwargs["pk"] = kwargs.get("pk", None)
        kwargs.pop("pk")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["full_name"] = kwargs["reporter_full_name"]
        context["company_relationship"] = kwargs["reporter_professional_relationship"]
        context["success_url"] = self.get_success_url()
        return context

    def get_success_url(self):
        return reverse(
            "confirmation",
            kwargs={"pk": self.request.session["breach_details_instance"]["report_id"]},
        )

    def post(self, request, *args, **kwargs):
        reference_id = str(uuid.uuid4()).split("-")[0]
        kwargs["reporter_confirmation_id"] = reference_id
        print(f"kwargs: {kwargs}")
        self.instance = BreachDetails(report_id=self.object.report_id)
        self.instance.reporter_confirmation_id = reference_id
        self.instance.save()
        return super().post(request, *args, **kwargs)


class ReportSubmissionCompleteView(TemplateView):
    """
    The final step in the reporting a breach application.
    This view will display the reporters reference number and information on the next steps in the process.
    """

    template_name = "confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_data = self.request.session.get("breach_details_instance")
        print(f"Session data - confirmation: {session_data}")
        context["service_header"] = SERVICE_HEADER
        context["application_reference_number"] = kwargs["reporter_confirmation_id"]
        return context
