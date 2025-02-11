from core.forms import BaseForm, BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Fluid, Layout, Size
from django import forms
from django.utils.timezone import now
from feedback.crispy_fields import get_field_with_label_id
from report_a_suspected_breach.fields import DateInputField
from report_a_suspected_breach.models import Breach
from report_a_suspected_breach.utils import get_active_regimes

Field.template = "core/custom_fields/field.html"


class WhenDidYouFirstSuspectForm(BaseModelForm):
    form_h1_header = "Date you first suspected the business or person had breached trade sanctions"
    bold_labels = False

    when_did_you_first_suspect = DateInputField(
        label="",
        help_text="For example, 17 06 2024",
        required=False,
        require_all_fields=True,
        error_messages={
            "incomplete": "Enter a full date including day, month and year",
            "invalid": "The date you first suspected the breach must be a real date",
        },
    )

    class Meta:
        model = Breach
        fields = ["when_did_you_first_suspect", "is_the_date_accurate"]
        widgets = {
            "is_the_date_accurate": forms.RadioSelect,
        }
        error_messages = {
            "is_the_date_accurate": {"required": "Select whether the date you entered was the exact date or an approximate date"},
        }
        labels = {
            "is_the_date_accurate": "Is the date you entered exact or approximate?",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = None
        self.helper.layout = Layout(
            Fieldset(
                Field("when_did_you_first_suspect", field_width=Fluid.ONE_HALF),
                legend="Enter the exact date or an approximate date",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Field.radios("is_the_date_accurate", legend_size=Size.MEDIUM, legend_tag="h2", inline=False),
        )
        self.fields["is_the_date_accurate"].choices.pop(0)

    def clean(self) -> dict[str, str]:
        cleaned_data = super().clean()
        if not cleaned_data.get("when_did_you_first_suspect") and "when_did_you_first_suspect" not in self.errors:
            # we only want to show the required error message if the date is not present
            self.add_error(
                "when_did_you_first_suspect",
                "Enter the date you first suspected the business or person had breached trade sanctions",
            )
        return cleaned_data

    def clean_when_did_you_first_suspect(self) -> str | None:
        when_did_you_first_suspect = self.cleaned_data["when_did_you_first_suspect"]
        if when_did_you_first_suspect:
            if when_did_you_first_suspect >= now().date():
                raise forms.ValidationError("The date you first suspected the breach must be in the past")
        return when_did_you_first_suspect


class WhichSanctionsRegimeForm(BaseForm):
    form_h1_header = "Which Sanctions Regime"

    which_sanctions_regime = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=(()),
        required=True,
        error_messages={
            "required": "Select the sanctions regime you suspect has been breached",
            "invalid": "Select the sanctions regime you suspect has been breached or select I do not know",
        },
    )

    class Media:
        js = ["report_a_suspected_breach/javascript/which_sanctions_regime.js"]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        checkbox_choices = []

        for item in get_active_regimes():
            checkbox_choices.append(Choice(item["name"], item["name"]))

        # adding the OR separator to the last option
        checkbox_choices[-1].divider = "or"

        checkbox_choices.append(Choice("Unknown Regime", "I do not know"))
        checkbox_choices.append(Choice("Other Regime", "Other regime"))
        self.fields["which_sanctions_regime"].choices = checkbox_choices
        self.fields["which_sanctions_regime"].label = False
        self.helper.label_size = None
        self.helper.label_tag = None
        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id("which_sanctions_regime", field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        if which_sanctions_regime := cleaned_data.get("which_sanctions_regime"):
            if ("Unknown Regime" in which_sanctions_regime or "Other Regime" in which_sanctions_regime) and len(
                which_sanctions_regime
            ) >= 2:
                # the user has selected "I do not know" and other regimes, this is an issue.
                # note that the user can select both "I do not know" and "Other Regime"
                self.add_error(
                    "which_sanctions_regime",
                    forms.ValidationError(
                        code="invalid", message=self.fields["which_sanctions_regime"].error_messages["invalid"]
                    ),
                )
        return cleaned_data


class WhatWereTheGoodsForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["what_were_the_goods"]
        labels = {
            "what_were_the_goods": "What were the goods or services, or what was the technological assistance or technology?",
        }
        help_texts = {
            "what_were_the_goods": "Give a short description. For example: accountancy services",
        }
        error_messages = {
            "what_were_the_goods": {
                "required": "Enter a short description of the goods, services, technological assistance or technology"
            },
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["what_were_the_goods"].widget.attrs = {"rows": 5}
