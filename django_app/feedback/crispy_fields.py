from typing import Any, Callable, Dict

from crispy_forms.layout import HTML
from crispy_forms_gds.layout import Field
from django.forms import Form
from django.template.loader import render_to_string
from django.utils.safestring import SafeString


class HTMLTemplate(HTML):
    """Renders an HTML template with a given context.

    This is useful for rendering custom HTML as part of a form without having to define the HTML in Python."""

    def __init__(self, html_template_path: str, html_context: Dict[str, Any] | None = None) -> None:
        if not html_context:
            html_context = {}

        self.html_template_path = html_template_path
        self.html_context = html_context

    def render(self, form: Form, context: dict | None = None, **kwargs: Any) -> SafeString:
        return render_to_string(self.html_template_path, self.html_context)


def get_field_with_label_id(*args: Any, field_method: Callable, label_id: str, **kwargs: Any) -> Field:
    """Returns a field with a label ID in the context"""
    field = field_method(*args, **kwargs)
    field.context.update({"label_id": label_id})
    return field
