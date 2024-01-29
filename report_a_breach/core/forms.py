from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout
from crispy_forms_gds.layout import Size
from crispy_forms_gds.layout import Submit
from django import forms

import report_a_breach.question_content as content
from report_a_breach.base_classes.forms import BaseModelForm

from .models import Breach

# TODO: check the wording of any error messages to match what the UCD team expect


class LandingForm(forms.ModelForm):
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


class StartForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_professional_relationship"]
        widgets = {"reporter_professional_relationship": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reporter_professional_relationship"].choices.pop(0)
        self.helper = FormHelper()
        self.helper.legend_size = Size.MEDIUM
        self.helper.layout = Layout(
            "reporter_professional_relationship", Submit("continue", "Continue")
        )


class EmailForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_email_address"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_email_address", Submit("continue", "Continue"))


class EmailVerifyForm(forms.Form):
    reporter_verify_email = forms.CharField(
        label=f"{content.VERIFY['text']}",
        help_text=f"{content.VERIFY['helper']}",
        widget=forms.TextInput(attrs={"id": "reporter_verify_email"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_verify_email", Submit("continue", "Continue"))


class NameForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_full_name"]
        widgets = {"reporter_full_name": forms.TextInput}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_full_name", Submit("continue", "Continue"))


class SummaryForm(BaseModelForm):
    class Meta:
        model = Breach
        exclude = [
            "reporter_full_name",
            "reporter_email_address",
            "reporter_professional_relationship",
            "additional_information",
        ]
