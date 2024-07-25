from django.http import HttpRequest


def get_dirty_form_data(request: HttpRequest, step_name: str) -> dict:
    """Get the dirty form data from the session."""
    return request.session.get(step_name, {})


def get_cleaned_data_for_step(request: HttpRequest, step_name: str) -> dict:
    """Helper function to get the cleaned data for a particular step"""
    from report_a_suspected_breach.urls import step_to_view_dict

    view_class = step_to_view_dict[step_name]
    form_class = view_class.form_class
    if not form_class:
        ...
    form = form_class(get_dirty_form_data(request, step_name), request=request)
    if form.is_valid():
        return form.cleaned_data
    else:
        return {}
