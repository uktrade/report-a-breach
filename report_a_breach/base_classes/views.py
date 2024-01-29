from django.views import View
from django.views.generic import FormView
from requests import Response

from report_a_breach.constants import SERVICE_HEADER


class BaseView(View):
    ...


class BaseFormView(BaseView, FormView):
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_header"] = SERVICE_HEADER
        return context

    def form_valid(self, form):
        form.save(commit=False)
        return super().form_valid(form)
        # return Response(self.get_success_url())
