from typing import Any

from crispy_forms.layout import HTML
from crispy_forms_gds.layout import Field
from django.forms import Form
from django.template.loader import render_to_string
from django.utils.safestring import SafeString


class FeedbackStars(Field):
    template = "feedback/crispy_fields/feedback_stars.html"
    css_class = None


class HTMLTemplate(HTML):
    """Renders an HTML template with a given context.

    This is useful for rendering custom HTML as part of a form without having to define the HTML in Python."""

    def __init__(self, html_template_path: str, html_context: str | None = None) -> None:
        if not html_context:
            html_context = {}

        self.html_template_path = html_template_path
        self.html_context = html_context

    def render(self, form: Form, context: dict | None = None, **kwargs: Any) -> SafeString:
        return render_to_string(self.html_template_path, self.html_context)


def get_textarea_field_with_label_id(*args: Any, label_id: str, **kwargs: Any) -> Field:
    """Returns a TextArea field with a label ID in the context - needed as the character count demands an
    aria-describedby attribute, which should be the ID of the label."""
    field = Field.textarea(*args, **kwargs)
    field.context.update({"label_id": label_id})
    return field