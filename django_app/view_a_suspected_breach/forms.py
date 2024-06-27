from core.forms import BaseForm
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout, Submit
from django import forms


class SelectForm(BaseForm):
    sort_by = forms.ChoiceField(
        choices=(
            ("date of report (newest)", "Date of report (newest)"),
            ("date of report (oldest)", "Date of report (oldest)"),
        ),
        label="Sort by",
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super(SelectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "sort_by",
            Submit("submit", "Submit"),
        )

    # def clean_sort_by(self) -> dict[str, Any]:
    #     sort_by = self.cleaned_data["sort_by"]
    #     breaches = Breach.objects.all()
    #     if sort_by["sort_by"] == "date of report (newest)":
    #         sorted_breaches = breaches.order_by("-created_by")
    #     else:
    #         sorted_breaches = breaches.order_by("created_by")
    #     sort_by["sort_by"] = sorted_breaches
    #     return sort_by
