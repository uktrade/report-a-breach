import re
from typing import Any

from core.forms import BaseModelForm
from django import forms
from utils.companies_house import get_formatted_address


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
            self.fields["country"].empty_label = "Select country"

        self.helper.label_size = None

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if self.is_uk_address:
            cleaned_data["country"] = "GB"
        cleaned_data["readable_address"] = get_formatted_address(cleaned_data)
        cleaned_data["is_uk_address"] = self.is_uk_address

        # we want to get the actual website address, not just the domain or whatever the user has inputted
        if website := cleaned_data.get("website"):
            cleaned_data["clickable_website_url"] = website if website.startswith("http") else f"https://{website}"

        return cleaned_data

    def clean_postal_code(self) -> dict[str, Any]:
        postal_code = self.cleaned_data.get("postal_code")
        if self.is_uk_address and postal_code:
            # we want to validate a UK postcode
            pattern = re.compile(r"^[A-Za-z]{1,2}\d[A-Za-z\d]? ?\d[A-Za-z]{2}$")
            if not pattern.match(postal_code):
                raise forms.ValidationError(code="invalid", message=self.fields["postal_code"].error_messages["invalid"])
        return postal_code
