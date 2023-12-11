import abc
from abc import ABC
from abc import abstractmethod

from crispy_forms_gds.layout import HTML
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView

from .constants import BREADCRUMBS_START_PAGE
from .constants import SERVICE_HEADER
from .forms import NameForm
from .forms import ProfessionalRelationshipForm


class StartView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context


class BaseFormView(FormView, ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        self.template_name = "form.html"
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context


class NameView(BaseFormView):
    def __init__(self, **kwargs):
        self.form_class = NameForm
        self.success_url = reverse_lazy("page_2")
        super().__init__(**kwargs)


class ProfessionalRelationshipView(BaseFormView):
    def __init__(self, **kwargs):
        self.form_class = ProfessionalRelationshipForm
        self.success_url = reverse_lazy("confirmation")
        super().__init__(**kwargs)


class ReportSubmissionCompleteView(TemplateView):
    template_name = "confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context
