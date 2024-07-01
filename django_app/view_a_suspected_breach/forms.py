from core.forms import BaseForm
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Field, Layout
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

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Field.select("sort_by"))
        self.fields["sort_by"].initial = str(kwargs.get("initial", {}).get("sort", "newest"))
