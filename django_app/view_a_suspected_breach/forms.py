from core.forms import BaseForm
from django import forms


class SelectForm(BaseForm):
    sort_by = forms.ChoiceField(
        choices=(
            ("newest", "Date of report (newest)"),
            ("oldest", "Date of report (oldest)"),
        ),
        label="Sort by",
        required=False,
    )
