from django.views import View
from django.views.generic import FormView
from requests import Response


class BaseView(View):
    ...


class BaseFormView(BaseView, FormView):
    def form_valid(self, form):
        form.save(commit=False)
        return Response(self.get_success_url())
