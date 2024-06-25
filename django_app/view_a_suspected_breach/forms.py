from core.forms import BaseForm
from crispy_forms_gds.layout import Field, Fluid, Layout
from django import forms


class WhichBreachReportForm(BaseForm):
    form_h1_header = "Suspected breach reports"
    search_bar = forms.CharField(
        label="Search by ID or name",
        max_length=100,
        required=False,
    )

    class Media:
        js = ("javascript/form_steps/which_sanctions_regimes.js",)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Field.text("search_bar", field_width=Fluid.THREE_QUARTERS),
        )
        self.helper.label_size = None
        self.helper.label_tag = None
