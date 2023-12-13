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
        print(breach_details_instance.report_id)
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
    success_url = reverse_lazy("confirmation")

    def get(self, request, *args, **kwargs):
        print(f"Session data: {self.request.session['breach_details_instance']}")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        reference_id = str(uuid.uuid4()).split("-")[0]
        breach_details_instance = form.save(commit=False)
        breach_details_instance.reporter_confirmation_id = reference_id
        breach_details_instance = form.save(commit=True)
        self.object = self.request.session.pop("breach_details_instance")
        self.object.save()
        return super().form_valid(form)

    # TODO: continue debug here, try to print the session data and pass that into the get method
    def get_form_kwargs(self, **kwargs):
        kwargs = self.kwargs
        print(kwargs)
        kwargs["reporter_confirmation_id"] = self.object.reporter_confirmation_id
        kwargs["reporter_full_name"] = self.object.reporter_full_name
        kwargs[
            "reporter_professional_relationship"
        ] = self.object.reporter_professional_relationship
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs = self.get_form_kwargs()
        context["full_name"] = kwargs["reporter_full_name"]
        context["company_relationship"] = self.object.reporter_professional_relationship
        print(f"object: {self.object.reporter_full_name}")
        print(type(self.object))
        print(f"kwargs: {kwargs['object'].reporter_full_name}")
        return context

    # def get_queryset(self):
    #     return BreachDetails.objects.filter(report_id=self.kwargs["pk"])

    # def get_object(self, queryset=None):
    #     report_param = self.kwargs.get("pk")
    #     return get_object_or_404(BreachDetails, report_id=report_param)


class ReportSubmissionCompleteView(TemplateView):
    """
    The final step in the reporting a breach application.
    This view will display the reporters reference number and information on the next steps in the process.
    """

    template_name = "confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        context["application_reference_number"] = self.request.session.get(
            "breach_details_instance"
        ).reporter_confirmation_id
        return context
