from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import StartForm


class StartView(FormView):
    template_name = "index.html"
    form_class = StartForm
    success_url = reverse_lazy("home")
