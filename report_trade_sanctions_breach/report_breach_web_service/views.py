from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView

from .constants import BREADCRUMBS_START_PAGE
from .constants import SERVICE_HEADER
from .forms import NameForm
from .forms import ProfessionalRelationshipForm
from .models import BreachDetails


class StartView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context


class BaseFormView(FormView):
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


class ProfessionalRelationshipView(BaseFormView):
    form_class = ProfessionalRelationshipForm
    success_url = reverse_lazy("confirmation")

    def __init__(self):
        super().__init__()


class ReportSubmissionCompleteView(TemplateView):
    template_name = "confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context
