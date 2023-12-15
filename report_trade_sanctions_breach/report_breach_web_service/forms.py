from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Button
from crispy_forms_gds.layout import Layout
from django import forms


# example taken from crispy-forms-gds tutorial
class StartForm(forms.Form):
    name = forms.CharField(
        label="Name",
        help_text="Your full name.",
        error_messages={"required": "Enter your name as it appears on your passport"},
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout("name", Button("submit", "Submit"))
        super().__init__(*args, **kwargs)


class ConfirmationForm(forms.Form):
    name = forms.CharField(
        label="Name",
        help_text="Your full name.",
        error_messages={"required": "Enter your name as it appears on your passport"},
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout("name", Button("submit", "Submit"))
        super().__init__(*args, **kwargs)
