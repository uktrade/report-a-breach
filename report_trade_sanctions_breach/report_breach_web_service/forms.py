from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Button
from crispy_forms_gds.layout import Field
from crispy_forms_gds.layout import Fieldset
from crispy_forms_gds.layout import Layout
from crispy_forms_gds.layout import Size
from django import forms
from django.utils.safestring import mark_safe

from .constants import PROFESSIONAL_RELATIONSHIP_CHOICES
from .models import BreachDetails


class NameForm(forms.ModelForm):
    reporter_full_name = forms.CharField(
        label=mark_safe("<strong>What is your full name</strong>"),
        error_messages={"required": "Enter your name as it appears on your passport"},
        widget=forms.TextInput(attrs={"id": "full_user_name"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_full_name", Button("continue", "Continue"))

    class Meta:
        model = BreachDetails
        fields = ["reporter_full_name"]


class ProfessionalRelationshipForm(forms.ModelForm):
    reporter_professional_relationship = forms.ChoiceField(
        choices=((choice, choice) for choice in PROFESSIONAL_RELATIONSHIP_CHOICES),
        widget=forms.RadioSelect,
        label=mark_safe(
            "<strong>What is the professional relationship with the company or person suspected of breaching "
            "sanctions?</strong>"
        ),
        error_messages={"required": "Please select one of the choices to continue"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # TODO: check why this helper isn't working
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            "reporter_professional_relationship", Button("continue", "Continue")
        )

    class Meta:
        model = BreachDetails
        fields = ["reporter_professional_relationship"]


class SummaryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Button("submit", "Submit"))

    class Meta:
        model = BreachDetails
        fields = ["reporter_full_name", "reporter_professional_relationship"]
