from django.forms import BaseForm
from django.http import HttpRequest


def get_dirty_form_data(request: HttpRequest, form_name: str) -> dict:
    return request.session.get(form_name, {})


def get_cleaned_form_data(request: HttpRequest, form_class: BaseForm) -> dict:
    form = form_class(get_dirty_form_data(request, form_class.__name__))

    if form.is_valid():
        return form.cleaned_data
    else:
        return {}


def get_cleaned_data_for_step(request: HttpRequest, step_name: str) -> dict:
    from report_a_suspected_breach.urls import step_to_view_dict

    view_class = step_to_view_dict[step_name]
    form_class = view_class.form_class
    return get_cleaned_form_data(request, form_class)
