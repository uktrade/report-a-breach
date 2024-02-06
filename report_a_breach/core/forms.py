from django import forms

import report_a_breach.question_content as content
from report_a_breach.base_classes.forms import BaseForm
from report_a_breach.base_classes.forms import BaseModelForm

from .models import Breach

# TODO: check the wording of any error messages to match what the UCD team expect


class StartForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_professional_relationship"]
        widgets = {"reporter_professional_relationship": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reporter_professional_relationship"].choices.pop(0)


class EmailForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_email_address"]


class EmailVerifyForm(BaseForm):
    reporter_verify_email = forms.CharField(
        label=f"{content.VERIFY['text']}",
        help_text=f"{content.VERIFY['helper']}",
    )

    def clean_reporter_verify_email(self):
        value = self.cleaned_data["reporter_verify_email"]
        if session_verify_code := self.request.session.get("verify_code"):
            if value != session_verify_code:
                raise forms.ValidationError("The code you entered is incorrect")
        else:
            raise Exception("No verify code in session")

        return value


class NameForm(BaseModelForm):
    reporter_full_name = forms.CharField(
        label=content.FULL_NAME["text"],
        widget=forms.TextInput(attrs={"id": "full_user_name"}),
    )

    class Meta:
        model = Breach
        fields = ["reporter_full_name"]
        widget = forms.TextInput(attrs={"id": "reporter_full_name"})


class SummaryForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["sanctions_regimes", "additional_information"]
