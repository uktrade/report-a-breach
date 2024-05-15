from feedback.crispy_fields import HTMLTemplate, get_textarea_field_with_label_id
from feedback.forms import FeedbackForm


def test_html_template():
    layout = HTMLTemplate(
        html_template_path="report_a_suspected_breach/complete.html",
        html_context={"request": {"session": {"reference_id": "123456"}}, "feedback_form": FeedbackForm()},
    )
    rendered = layout.render(FeedbackForm())
    assert "123456" in rendered


def test_get_textarea_field_with_label_id():
    field = get_textarea_field_with_label_id("test_field", label_id="test_id")
    assert field.context["label_id"] == "test_id"
