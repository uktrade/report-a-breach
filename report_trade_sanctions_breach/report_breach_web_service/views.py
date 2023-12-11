from crispy_forms_gds.layout import HTML
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView

from .constants import BREADCRUMBS_START_PAGE
from .constants import SERVICE_HEADER
from .forms import StartForm


class StartView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = BREADCRUMBS_START_PAGE
        return context


class FirstFormView(FormView):
    template_name = "form.html"
    form_class = StartForm
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context
