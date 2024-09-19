from core.forms import BaseForm
from django import forms


class DeclarationForm(BaseForm):
    submit_button_text = "Submit"
    declaration = forms.BooleanField(
        label="I agree and accept", required=True, error_messages={"required": "Confirm if you agree and accept the declaration"}
    )
