from typing import Any

from core.forms import BaseForm
from django import forms
from report_a_suspected_breach.models import Breach


class WhichBreachReportForm(BaseForm):
    which_breach_report = forms.CharField(
        label="Which Sanctions Breach Report would you like to view?",
        help_text="Please enter the reference id obtained from the email",
        error_messages={"required": "Check your email or contact an administrator if you do not have the reports reference id"},
    )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        which_breach_report = cleaned_data.get("which_breach_report")
        try:
            Breach.objects.get(reference=which_breach_report)
        except Breach.DoesNotExist:
            raise forms.ValidationError("That requested report does not exist")

        return cleaned_data
