from crispy_forms_gds.layout import Layout
from crispy_forms_gds.layout import Size
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
        self.helper.legend_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_professional_relationship")


class EmailForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_email_address"]
        widget = forms.TextInput(attrs={"id": "email_address"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_email_address")


class EmailVerifyForm(BaseForm):
    reporter_verify_email = forms.CharField(
        label=f"{content.VERIFY['text']}",
        help_text=f"{content.VERIFY['helper']}",
        widget=forms.TextInput(attrs={"id": "verify_email"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_verify_email")


class NameForm(BaseModelForm):
    reporter_full_name = forms.CharField(
        label=content.FULL_NAME["text"],
        widget=forms.TextInput(attrs={"id": "full_user_name"}),
    )

    class Meta:
        model = Breach
        fields = ["reporter_full_name"]
        widget = forms.TextInput(attrs={"id": "reporter_full_name"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout("reporter_full_name")


class SummaryForm(BaseModelForm):
    class Meta:
        model = Breach
        exclude = [
            "reporter_full_name",
            "reporter_email_address",
            "reporter_professional_relationship",
            "additional_information",
        ]
