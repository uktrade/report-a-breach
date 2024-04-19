from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout, Size, Submit
from django import forms
from utils.companies_house import get_formatted_address


class EmptyForm(forms.Form):
    pass


class BaseForm(forms.Form):
    bold_labels = True
    form_h1_header = None
    single_question_form = False
    show_back_button = True
    # fields that you don't want to display (optional) next to the label if they're not required
    hide_optional_label_fields = []
    # if we're using a BaseForm and NOT a BaseModelForm, then we need to implement our own labels dictionary to set the labels
    labels = {}
    # same for help_texts
    help_texts = {}
    # do we want this form to be revalidated when the user clicks Done
    revalidate_on_done = True

    class Media:
        css = {
            "all": ["form.css"],
        }

    def __init__(self, address_string=None, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.form_h1_header = kwargs.pop("form_h1_header", self.form_h1_header)
        super().__init__(*args, **kwargs)

        if len(self.fields) == 1:
            self.single_question_form = True

        for field_name, label in self.labels.items():
            self.fields[field_name].label = label

        for field_name, help_text in self.help_texts.items():
            self.fields[field_name].help_text = help_text

        self.helper = FormHelper()
        self.helper.add_input(Submit("continue", "Continue", css_class="btn-primary"))

        if self.single_question_form and not self.form_h1_header:
            self.helper.label_tag = "h1"
            self.helper.legend_tag = "h1"
            self.helper.legend_size = Size.LARGE

        if self.bold_labels:
            self.helper.label_size = Size.LARGE

        self.helper.layout = Layout(*self.fields)


class BaseModelForm(BaseForm, forms.ModelForm):
    pass


class BasePersonBusinessDetailsForm(BaseModelForm):
    """A base form for capturing personal or business details. Such as the End-User Form and the BusinessOrPersonDetails Form."""

    class Meta:
        widgets = {
            "name": forms.TextInput,
            "website": forms.TextInput,
            "country": forms.Select,
            "address_line_1": forms.TextInput,
            "address_line_2": forms.TextInput,
            "address_line_3": forms.TextInput,
            "address_line_4": forms.TextInput,
            "town_or_city": forms.TextInput,
            "county": forms.TextInput,
            "postal_code": forms.TextInput,
        }
        labels = {
            "name": "Name of business or person",
            "website": "Website address",
            "country": "Country",
            "address_line_1": "Address line 1",
            "address_line_2": "Address line 2",
            "address_line_3": "Address line 3",
            "address_line_4": "Address line 4",
            "town_or_city": "Town or city",
            "county": "County",
            "postal_code": "Postcode",
        }

    readable_address = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.is_uk_address = kwargs.pop("is_uk_address", False)
        super().__init__(*args, **kwargs)
        if self.is_uk_address:
            self.fields["country"].initial = "GB"
            self.fields["country"].widget = forms.HiddenInput()
            del self.fields["address_line_3"]
            del self.fields["address_line_4"]
        else:
            del self.fields["postal_code"]
            del self.fields["county"]
            self.fields["town_or_city"].required = False
            self.fields["address_line_1"].required = False

        self.helper.label_size = None

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["readable_address"] = get_formatted_address(cleaned_data)
        return cleaned_data
