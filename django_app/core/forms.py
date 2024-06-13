import re
from typing import Any

from crispy_forms_gds.choices import Choice
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Field, Layout, Size, Submit
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
    # the submit button text
    submit_button_text = "Continue"

    class Media:
        css = {
            "all": ["form.css"],
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
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
        self.helper.add_input(Submit("continue", self.submit_button_text, css_class="btn-primary"))

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
        error_messages = {
            "name": {"required": "Enter the name of the business or person"},
            "address_line_1": {"required": "Enter address line 1, such as the building and street"},
            "town_or_city": {"required": "Enter town or city"},
            "postal_code": {"required": "Enter postcode", "invalid": "Enter a full UK postcode"},
            "country": {"required": "Select country"},
        }

    readable_address = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args: object, **kwargs: object) -> None:
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
            self.fields["country"].required = True

        self.helper.label_size = None

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if self.is_uk_address:
            cleaned_data["country"] = "GB"
        cleaned_data["readable_address"] = get_formatted_address(cleaned_data)
        return cleaned_data

    def clean_postal_code(self) -> dict[str, Any]:
        postal_code = self.cleaned_data.get("postal_code")
        if self.is_uk_address and postal_code:
            # we want to validate a UK postcode
            pattern = re.compile(r"^[A-Za-z]{1,2}\d[A-Za-z\d]? ?\d[A-Za-z]{2}$")
            if not pattern.match(postal_code):
                raise forms.ValidationError(code="invalid", message=self.fields["postal_code"].error_messages["invalid"])
        return postal_code


class CookiesConsentForm(BaseForm):
    do_you_want_to_accept_analytics_cookies = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        widget=forms.RadioSelect,
        label="Do you want to accept analytics cookies",
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("save cookie settings", "Save cookie settings", css_class="govuk-button"))
        self.helper.layout = Layout(
            Field.radios("do_you_want_to_accept_analytics_cookies", legend_size=Size.MEDIUM, legend_tag="h2", inline=False)
        )
        # Allows us to display to the user their previously selected cookies choice in the radios
        kwargs_initial = kwargs.get("initial")
        if kwargs_initial:
            self.fields["do_you_want_to_accept_analytics_cookies"].initial = str(kwargs_initial["accept_cookies"])


class HideCookiesForm(BaseForm):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("hide cookie message", "Hide cookie message", css_class="govuk-button"))
