from django.http import HttpRequest


def get_dirty_form_data(request: HttpRequest, step_name: str) -> dict:
    """Get the dirty form data from the session."""
    return request.session.get(step_name, {})


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


def get_form(request: HttpRequest, step_name: str) -> dict:
    from report_a_suspected_breach.urls import step_to_view_dict

    view_class = step_to_view_dict[step_name]
    form_class = view_class.form_class
    form = form_class(get_dirty_form_data(request, step_name), request=request)
    if form.is_valid():
        return form
    else:
        return {}


def get_active_regimes() -> list[dict[str, str]]:
    """Get the active sanctions regimes. If submodule is not present, return an empty list."""
    try:
        from sanctions_regimes.report_a_breach import active_regimes
    except ImportError:
        active_regimes = []

    return active_regimes
