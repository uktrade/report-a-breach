from django.urls import reverse_lazy
from django.views.generic import FormView

from .constants import TITLE
from .forms import StartForm


class StartView(FormView):
    form_title = TITLE
    template_name = "index.html"
    form_class = StartForm
    success_url = reverse_lazy("home")
