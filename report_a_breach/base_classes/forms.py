from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Submit
from django import forms


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))


class BaseModelForm(BaseForm, forms.ModelForm):
    ...
