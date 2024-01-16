from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Button
from crispy_forms_gds.layout import Layout
from crispy_forms_gds.layout import Size
from django import forms
from django.utils.safestring import mark_safe

from .constants import PROFESSIONAL_RELATIONSHIP_CHOICES
from .models import BreachDetails


class StartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Button("start now", "Start now"))

    class Meta:
        model = BreachDetails
        exclude = [
            "reporter_full_name",
            "reporter_email_address",
            "reporter_professional_relationship",
        ]


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


class EmailForm(forms.ModelForm):
    reporter_email_address = forms.EmailField(
        label=mark_safe("<strong>What is your email address</strong>"),
        error_messages={"required": "We need to send you an email to verify your email address"},
        widget=forms.TextInput(attrs={"id": "reporter_email_address"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_email_address", Button("continue", "Continue"))

    class Meta:
        model = BreachDetails
        fields = ["reporter_email_address"]


class EmailVerifyForm(forms.ModelForm):
    reporter_verify_email = forms.CharField(
        # TODO: need to fix the label to specify in smaller print, req: 6 digit...
        label=mark_safe("<strong>We've sent you an email</strong>"),
        help_text="Enter the 6 digit security code",
        error_messages={"required": "Please enter the 6 digit security code provided in the email"},
        widget=forms.TextInput(attrs={"id": "reporter_verify_email"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_verify_email", Button("continue", "Continue"))

    class Meta:
        model = BreachDetails
        exclude = [
            "reporter_full_name",
            "reporter_email_address",
            "reporter_professional_relationship",
        ]


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
        exclude = [
            "reporter_email_address",
            "reporter_full_name",
            "reporter_professional_relationship",
        ]
