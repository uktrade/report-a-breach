from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import HTML
from crispy_forms_gds.layout import Button
from crispy_forms_gds.layout import Layout
from crispy_forms_gds.layout import Size
from django import forms
from django.utils.safestring import mark_safe

from .constants import PROFESSIONAL_RELATIONSHIP_CHOICES


class NameForm(forms.Form):
    name = forms.CharField(
        label=mark_safe("<strong>What is your full name</strong>"),
        error_messages={"required": "Enter your name as it appears on your passport"},
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("name", Button("continue", "Continue"))
        super().__init__(*args, **kwargs)


class ProfessionalRelationshipForm(forms.Form):
    name = forms.ChoiceField(
        choices=((choice, choice) for choice in PROFESSIONAL_RELATIONSHIP_CHOICES),
        widget=forms.RadioSelect,
        label="What is the professional relationship with the company or person suspected of breaching sanctions?",
        error_messages={"required": "Please select one of the choices to continue"},
    )

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout("name", Button("continue", "Continue"))
        super().__init__(*args, **kwargs)
