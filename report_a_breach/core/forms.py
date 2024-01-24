from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Button
from crispy_forms_gds.layout import Layout
from crispy_forms_gds.layout import Size
from django import forms
from django.utils.safestring import mark_safe

# from report_a_breach.constants import PROFESSIONAL_RELATIONSHIP_CHOICES
import report_a_breach.question_content as content

from .models import Breach


class StartForm(forms.ModelForm):
    class Meta:
        model = Breach
        fields = [
            "reporter_professional_relationship",
        ]


class NameForm(forms.ModelForm):
    reporter_full_name = forms.CharField(
        label=mark_safe("<strong>What is your full name</strong>"),
        error_messages={"required": "Please enter your name as it appears on your passport"},
        widget=forms.TextInput(attrs={"id": "full_user_name"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_full_name", Button("continue", "Continue"))

    class Meta:
        model = Breach
        fields = ["reporter_full_name"]


class EmailForm(forms.Form):
    field = forms.EmailField(
        label=mark_safe(f"{content.EMAIL['text']}"),
        error_messages={"required": "We need to send you an email to verify your email address"},
        help_text=content.EMAIL["helper"],
        widget=forms.TextInput(attrs={"class": "govuk-input"}),
        max_length=55,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        return cleaned_data


class EmailVerifyForm(forms.Form):
    field = forms.CharField(
        label=mark_safe(f"<strong>{content.VERIFY['text']}</strong>"),
        help_text=content.VERIFY["helper"],
        error_messages={"required": "Please enter the 6 digit security code provided in the email"},
        widget=forms.TextInput(attrs={"id": "reporter_verify_email"}),
    )


# class ProfessionalRelationshipForm(forms.ModelForm):
#     reporter_professional_relationship = forms.ChoiceField(
#         choices=((choice, choice) for choice in PROFESSIONAL_RELATIONSHIP_CHOICES),
#         widget=forms.RadioSelect,
#         label=mark_safe(
#             "<strong>What is the professional relationship with the company or person suspected of breaching "
#             "sanctions?</strong>"
#         ),
#         error_messages={"required": "Please select one of the choices to continue"},
#     )
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         # TODO: check why this helper isn't working
#         self.helper.label_size = Size.MEDIUM
#         self.helper.layout = Layout(
#             "reporter_professional_relationship", Button("continue", "Continue")
#         )
#
#     class Meta:
#         model = Breach
#         fields = ["reporter_professional_relationship"]


class SummaryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Button("submit", "Submit"))

    class Meta:
        model = Breach
        exclude = [
            "reporter_email_address",
            "reporter_full_name",
            "reporter_professional_relationship",
        ]
