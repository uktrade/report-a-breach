from django import forms


class BaseForm(forms.Form):
    ...


class BaseModelForm(BaseForm, forms.ModelForm):
    ...
