from django.views import View
from django.views.generic import FormView


class BaseView(View):
    ...


class BaseFormView(BaseView, FormView):
    ...
