from crispy_forms_gds.helper import FormHelper
from django import forms


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class BaseModelForm(BaseForm, forms.ModelForm):
    ...
