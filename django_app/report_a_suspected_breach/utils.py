from typing import List

from django.http import HttpRequest


def get_dirty_form_data(request: HttpRequest, step_name: str) -> dict:
    """Get the dirty form data from the session."""
    return request.session.get(step_name, {})


def get_required_fields(request: HttpRequest, step_name: str) -> List:
    """Get the required fields from the form."""
    from report_a_suspected_breach.urls import step_to_view_dict

    view_class = step_to_view_dict[step_name]
    form_class = view_class.form_class
    form = form_class(get_dirty_form_data(request, step_name), request=request)
    required_fields = []
    for field_name, field in form.fields.items():
        if field.required:
            required_fields.append(field_name)
    return required_fields


def get_cleaned_data_for_step(request: HttpRequest, step_name: str) -> dict:
    """Helper function to get the cleaned data for a particular step"""
    from report_a_suspected_breach.urls import step_to_view_dict

    view_class = step_to_view_dict[step_name]
    form_class = view_class.form_class
    form = form_class(get_dirty_form_data(request, step_name), request=request)
    if form.is_valid():
        return form.cleaned_data
    else:
        return {}


def get_all_cleaned_data(request: HttpRequest) -> dict:
    """Helper function to get all the cleaned data from the session"""
    from report_a_suspected_breach.urls import step_to_view_dict

    all_cleaned_data = {}
    form_views = [step for step, view in step_to_view_dict.items() if getattr(view, "form_class", None)]
    for step_name in form_views:
        all_cleaned_data[step_name] = get_cleaned_data_for_step(request, step_name)

    return all_cleaned_data


def get_all_required_views() -> List[str]:
    """Helper function to get all the required fields from the forms"""
    from report_a_suspected_breach.urls import step_to_view_dict

    required_views = [
        step for step, view in step_to_view_dict.items() if getattr(view, "form_class", None) and view.required_step
    ]

    return required_views


def get_all_required_fields(request: HttpRequest) -> dict:
    """Helper function to get all the required fields from the views"""
    required_fields = {}
    required_views = get_all_required_views()
    for step_name in required_views:
        required_fields[step_name] = get_required_fields(request, step_name)
    return required_fields


def get_missing_data(request: HttpRequest) -> dict:
    cleaned_data = get_all_cleaned_data(request)
    required_fields = get_all_required_fields(request)
    missing_data = {}
    for step_name in required_fields:
        missing_step_data = set(required_fields[step_name]) - set(cleaned_data[step_name])
        if missing_step_data:
            missing_data[step_name] = missing_step_data
    return missing_data
