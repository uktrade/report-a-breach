from crispy_forms_gds.layout import HTML
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView

from .constants import SERVICE_HEADER
from .forms import StartForm


class StartView(FormView):
    template_name = "index.html"
    form_class = StartForm
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context
