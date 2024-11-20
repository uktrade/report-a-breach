from typing import Any

from core.forms import BaseForm, BaseModelForm
from crispy_forms_gds.layout import (
    ConditionalQuestion,
    ConditionalRadios,
    Field,
    Fieldset,
    Fluid,
    Layout,
    Size,
)
from django import forms
from django_countries import countries
from report_a_suspected_breach.exceptions import (
    CompaniesHouse500Error,
    CompaniesHouseException,
)
from report_a_suspected_breach.forms.base_forms import BasePersonBusinessDetailsForm
from report_a_suspected_breach.models import Breach, PersonOrCompany
from utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)

Field.template = "core/custom_fields/field.html"


class AreYouReportingABusinessOnCompaniesHouseForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["business_registered_on_companies_house"]
        widgets = {"business_registered_on_companies_house": forms.RadioSelect}
        labels = {
            "business_registered_on_companies_house": "Are you reporting a business which is registered with UK Companies House?"
        }
        error_messages = {
            "business_registered_on_companies_house": {
                "required": "Select yes if you are reporting a business which is registered with UK Companies House"
            }
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["business_registered_on_companies_house"].choices.pop(0)


class DoYouKnowTheRegisteredCompanyNumberForm(BaseModelForm):
    hide_optional_label_fields = ["registered_company_number"]

    registered_company_name = forms.CharField(required=False)
    registered_office_address = forms.CharField(required=False)

    class Meta:
        model = PersonOrCompany
        fields = ["do_you_know_the_registered_company_number", "registered_company_number"]
        widgets = {"do_you_know_the_registered_company_number": forms.RadioSelect}
        labels = {
            "do_you_know_the_registered_company_number": "Do you know the registered company number?",
            "registered_company_number": "Registered company number",
        }
        error_messages = {
            "do_you_know_the_registered_company_number": {"required": "Select yes if you know the registered company number"},
            "registered_company_number": {
                "required": "Enter the registered company number",
                "invalid": "Number not recognised with Companies House. Enter the correct registered company number. "
                # changed from 8 numbers to 8 charcaters
                "This should be 8 characters long.",
            },
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # emptying the form if the user has requested to change the details
        if self.request.GET.get("change") == "yes" and self.request.method == "GET":
            self.is_bound = False
            self.data = {}

        # todo - abstract the following logic to apply to all ConditionalRadios forms
        self.helper.legend_tag = "h1"
        self.helper.legend_size = Size.LARGE
        self.helper.label_tag = ""
        self.helper.label_size = None
        self.helper.layout = Layout(
            ConditionalRadios(
                "do_you_know_the_registered_company_number",
                ConditionalQuestion(
                    "Yes",
                    Field.text("registered_company_number", field_width=Fluid.ONE_THIRD),
                ),
                "No",
            )
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        do_you_know_the_registered_company_number = cleaned_data.get("do_you_know_the_registered_company_number")
        registered_company_number = cleaned_data.get("registered_company_number")
        if do_you_know_the_registered_company_number == "yes":
            if not registered_company_number:
                self.add_error(
                    "registered_company_number",
                    forms.ValidationError(
                        code="required", message=self.Meta.error_messages["registered_company_number"]["required"]
                    ),
                )
                # we don't need to continue if the company number is missing
                return cleaned_data

            registered_company_number = registered_company_number.strip().upper()

            # todo: companies house have updated their API so an invalid number returns 500.
            #  Issue-tracker: https://forum.aws.chdev.org/t/non-existing-company-number-returns-500/8468

            if len(registered_company_number) == 8 and registered_company_number.isalnum():
                # Re-checking companies house API, so remove 500
                self.request.session.pop("company_details_500", None)
                try:
                    company_details = get_details_from_companies_house(registered_company_number)
                    cleaned_data["registered_company_number"] = company_details["company_number"]
                    cleaned_data["registered_company_name"] = company_details["company_name"]

                    address = company_details["registered_office_address"]
                    country = address.get("country")
                    COUNTRY_DICT = dict(countries)

                    if country in ["England", "Northern Ireland", "Scotland", "Wales", "United Kingdom", "England/Wales"]:
                        address["country"] = "United Kingdom"
                    elif country in COUNTRY_DICT.values():
                        country_code = next((code for code, name in COUNTRY_DICT.items() if name == country), None)
                        if country_code:
                            address["country"] = COUNTRY_DICT[country_code]

                    cleaned_data["registered_office_address"] = get_formatted_address(
                        company_details["registered_office_address"]
                    )
                except CompaniesHouseException:
                    self.add_error(
                        "registered_company_number",
                        forms.ValidationError(
                            code="invalid", message=self.Meta.error_messages["registered_company_number"]["invalid"]
                        ),
                    )
                except CompaniesHouse500Error:
                    self.request.session["company_details_500"] = True
                    self.request.session.modified = True
            else:
                self.add_error(
                    "registered_company_number",
                    forms.ValidationError(
                        code="invalid", message=self.Meta.error_messages["registered_company_number"]["invalid"]
                    ),
                )
        return cleaned_data


class ManualCompaniesHouseInputForm(BaseForm):
    manual_companies_house_input = forms.ChoiceField(
        label="Where is the business located?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select if the address of the business suspected of "
            "breaching sanctions is in the UK, or outside the UK"
        },
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                Field.radios(
                    "manual_companies_house_input",
                    legend_size=Size.MEDIUM,
                )
            )
        )


class WhereIsTheAddressOfTheBusinessOrPersonForm(BaseForm):
    where_is_the_address = forms.ChoiceField(
        label="Where is the address of the business or person suspected of breaching sanctions?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select if the address of the business or person suspected of "
            "breaching sanctions is in the UK, or outside the UK"
        },
    )


class BusinessOrPersonDetailsForm(BasePersonBusinessDetailsForm):
    form_h1_header = "Business or person details"

    class Meta(BasePersonBusinessDetailsForm.Meta):
        model = PersonOrCompany
        fields = [
            "name",
            "website",
            "country",
            "town_or_city",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postal_code",
        ]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.TWO_THIRDS),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("website", field_width=Fluid.TWO_THIRDS),
                legend="Website",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_3", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_4", field_width=Fluid.TWO_THIRDS),
                Field.text("town_or_city", field_width=Fluid.ONE_HALF if self.is_uk_address else Fluid.TWO_THIRDS),
                Field.text("county", field_width=Fluid.ONE_HALF),
                Field.text("postal_code", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
        )
