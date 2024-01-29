from django import forms

import report_a_breach.question_content as content

from .models import Breach


# TODO: check the wording of any error messages to match what the UCD team expect


class HomeForm(forms.ModelForm):
    class Meta:
        model = Breach
        # TODO: should this log a "self report" to initialize the DB and generate the pk?
        exclude = [
            "reporter_full_name",
            "reporter_email_address",
            "reporter_professional_relationship",
            # "sanctions_regimes",
            "additional_information",
        ]


class EmailForm(forms.Form):
    field = forms.EmailField(
        label=content.EMAIL["text"],
        error_messages={"required": "We need to send you an email to verify your email address"},
        help_text=content.EMAIL["helper"],
        widget=forms.TextInput(attrs={"name": "email address"}),
        required=True,
    )


class EmailVerifyForm(forms.Form):
    field = forms.CharField(
        label=content.VERIFY["text"],
        help_text=content.VERIFY["helper"],
        error_messages={"required": "Please enter the 6 digit security code provided in the email"},
        widget=forms.TextInput(attrs={"name": "verify code"}),
    )


class NameForm(forms.Form):
    field = forms.CharField(
        label=content.FULL_NAME["text"],
        help_text=content.FULL_NAME["helper"],
        error_messages={"required": "Please enter your name as it appears on your passport"},
        widget=forms.TextInput(attrs={"name": "full name"}),
    )


class ProfessionalRelationshipForm(forms.Form):
    # TODO: radio size is showing as small. CSS appears ok. Might be possible to access the radio size in the form
    field = forms.ChoiceField(
        choices=((choice[1], choice[1]) for choice in content.RELATIONSHIP["choices"]),
        widget=forms.RadioSelect(attrs={"name": "company professional relationship"}),
        label=content.RELATIONSHIP["text"],
        error_messages={"required": "Please select one of the choices to continue"},
    )


class SummaryForm(forms.ModelForm):
    class Meta:
        model = Breach
        exclude = [
            "reporter_full_name",
            "reporter_email_address",
            "reporter_professional_relationship",
            "additional_information",
        ]
