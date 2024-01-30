from django.views.generic import FormView
from requests import Response


class BaseView(FormView):
    template_name = "form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BaseModelFormView(BaseView):
    def form_valid(self, form):
        form.save(commit=False)
        return super().form_valid(form)
        # return Response(self.get_success_url())
