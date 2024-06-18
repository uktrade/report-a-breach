import os
from datetime import timedelta
from typing import Any

from core.document_storage import TemporaryDocumentStorage
from core.forms import BaseForm, BaseModelForm, BasePersonBusinessDetailsForm
from core.utils import get_mime_type, is_request_ratelimited
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.helper import FormHelper
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
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.html import escape
from django.utils.timezone import now
from django_chunk_upload_handlers.clam_av import VirusFoundInFileException
from feedback.crispy_fields import HTMLTemplate, get_field_with_label_id
from utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)
from utils.s3 import get_all_session_files

from .choices import IsTheDateAccurateChoices
from .exceptions import CompaniesHouseException
from .fields import DateInputField, MultipleFileField
from .models import (
    Breach,
    PersonOrCompany,
    ReporterEmailVerification,
    SanctionsRegime,
    UploadedDocument,
)

# TODO: check the wording of any error messages to match what the UCD team expect
Field.template = "core/custom_fields/field.html"


class StartForm(BaseModelForm):
    show_back_button = False

    class Meta:
        model = Breach
        fields = ["reporter_professional_relationship"]
        error_messages = {
            "reporter_professional_relationship": {
                "required": "Select your professional relationship with the business or person suspected of breaching sanctions"
            }
        }
        widgets = {"reporter_professional_relationship": forms.RadioSelect}
        labels = {
            "reporter_professional_relationship": "What is your professional relationship with "
            "the business or person suspected of breaching sanctions?",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["reporter_professional_relationship"].choices.pop(0)


class EmailForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_email_address"]
        help_texts = {
            "reporter_email_address": "We need to send you an email to verify your email address.",
        }
        labels = {
            "reporter_email_address": "What is your email address?",
        }
        error_messages = {
            "reporter_email_address": {
                "required": "Enter your email address",
                "invalid": "Enter an email in the correct format, for example name@example.com",
            },
        }


class EmailVerifyForm(BaseForm):
    bold_labels = False
    form_h1_header = "We've sent you an email"
    revalidate_on_done = False

    email_verification_code = forms.CharField(
        label="Enter the 6 digit security code",
        error_messages={"required": "Enter the 6 digit security code we sent to your email"},
    )

    def clean_email_verification_code(self) -> str:
        # first we check if the request is rate-limited
        if is_request_ratelimited(self.request):
            raise forms.ValidationError("You've tried to verify your email too many times. Try again in 1 minute")

        email_verification_code = self.cleaned_data["email_verification_code"]
        email_verification_code = email_verification_code.replace(" ", "")

        verify_timeout_seconds = settings.EMAIL_VERIFY_TIMEOUT_SECONDS

        verification_object = ReporterEmailVerification.objects.filter(reporter_session=self.request.session.session_key).latest(
            "date_created"
        )
        self.verification_object = verification_object
        verify_code = verification_object.email_verification_code
        if email_verification_code != verify_code:
            raise forms.ValidationError("Code is incorrect. Enter the 6 digit security code we sent to your email")

        # check if the user has submitted the verify code within the specified timeframe
        allowed_lapse = verification_object.date_created + timedelta(seconds=verify_timeout_seconds)
        if allowed_lapse < now():
            raise forms.ValidationError("The code you entered is no longer valid. Please verify your email again")

        return email_verification_code

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.request = kwargs.pop("request") if "request" in kwargs else None
        request_verify_code = reverse_lazy("report_a_suspected_breach:request_verify_code")
        self.helper["email_verification_code"].wrap(
            Field,
            HTMLTemplate(
                "report_a_suspected_breach/form_steps/partials/not_received_code_help_text.html",
                {"request_verify_code": request_verify_code},
            ),
        )


class NameForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_full_name"]
        labels = {
            "reporter_full_name": "What is your full name?",
        }
        error_messages = {
            "reporter_full_name": {"required": "Enter your full name"},
        }


class NameAndBusinessYouWorkForForm(BaseModelForm):
    form_h1_header = "Your details"

    class Meta:
        model = Breach
        fields = ["reporter_full_name", "reporter_name_of_business_you_work_for"]
        labels = {
            "reporter_full_name": "Full name",
            "reporter_name_of_business_you_work_for": "Business you work for",
        }
        help_texts = {
            "reporter_name_of_business_you_work_for": "This is the business that employs you, not the business you're reporting",
        }
        error_messages = {
            "reporter_full_name": {"required": "Enter your full name"},
            "reporter_name_of_business_you_work_for": {"required": "Enter the name of the business you work for"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = None
        self.helper.layout = Layout(
            Field.text("reporter_full_name", field_width=Fluid.ONE_HALF),
            Field.text("reporter_name_of_business_you_work_for", field_width=Fluid.ONE_HALF),
        )


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
                "This is usually an 8-digit number.",
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

            # now we need to get the company details from Companies House
            # and store them in the form. First we check the request session to see if
            # they're already been obtained
            if session_company_details := self.request.session.get("company_details"):
                if cleaned_data["registered_company_number"] == session_company_details["registered_company_number"]:
                    cleaned_data["registered_company_name"] = session_company_details["registered_company_name"]
                    cleaned_data["registered_office_address"] = session_company_details["registered_office_address"]
                    return cleaned_data

            try:
                company_details = get_details_from_companies_house(registered_company_number)
                cleaned_data["registered_company_number"] = company_details["company_number"]
                cleaned_data["registered_company_name"] = company_details["company_name"]
                cleaned_data["registered_office_address"] = get_formatted_address(company_details["registered_office_address"])
            except CompaniesHouseException:
                self.add_error(
                    "registered_company_number",
                    forms.ValidationError(
                        code="invalid", message=self.Meta.error_messages["registered_company_number"]["invalid"]
                    ),
                )

        return cleaned_data


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
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "town_or_city",
            "county",
            "postal_code",
        ]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.ONE_HALF),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("website", field_width=Fluid.ONE_HALF),
                legend="Website",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("county", field_width=Fluid.ONE_THIRD),
                Field.text("postal_code", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
        )


class AboutTheSupplierForm(BusinessOrPersonDetailsForm):
    form_h1_header = "About the supplier"

    class Meta(BusinessOrPersonDetailsForm.Meta):
        model = BusinessOrPersonDetailsForm.Meta.model
        fields = BusinessOrPersonDetailsForm.Meta.fields
        labels = BusinessOrPersonDetailsForm.Meta.labels
        widgets = BusinessOrPersonDetailsForm.Meta.widgets


class WhenDidYouFirstSuspectForm(BaseModelForm):
    form_h1_header = "Date you first suspected the business or person had breached trade sanctions"
    bold_labels = False

    when_did_you_first_suspect = DateInputField(
        label="",
        help_text="For example, 17 06 2024",
        required=False,
        require_all_fields=True,
        error_messages={
            "incomplete": "Enter a full date including day, month and year",
            "invalid": "The date you first suspected the breach must be a real date",
        },
    )

    class Meta:
        model = Breach
        fields = ["when_did_you_first_suspect", "is_the_date_accurate"]
        widgets = {
            "is_the_date_accurate": forms.RadioSelect,
        }
        error_messages = {
            "is_the_date_accurate": {"required": "Select whether you know the exact date, or the approximate date"},
        }
        labels = {
            "is_the_date_accurate": "Is the date you entered exact or approximate?",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = None
        self.helper.layout = Layout(
            Fieldset(
                Field("when_did_you_first_suspect", field_width=Fluid.ONE_HALF),
                legend="Enter the exact date or an approximate date",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Field.radios("is_the_date_accurate", legend_size=Size.MEDIUM, legend_tag="h2", inline=False),
        )
        self.fields["is_the_date_accurate"].choices.pop(0)

    def clean(self) -> dict[str, str]:
        cleaned_data = super().clean()
        if is_the_date_accurate := cleaned_data.get("is_the_date_accurate"):
            when_did_you_first_suspected = cleaned_data.get("when_did_you_first_suspect")
            if not self["when_did_you_first_suspect"].errors:
                # if the date has been entered but just isn't valid, we don't want to show the 'required' error.
                # invalid dates are not part of cleaned_data, so we can't see them here

                if is_the_date_accurate == IsTheDateAccurateChoices.exact and not when_did_you_first_suspected:
                    self.add_error("when_did_you_first_suspect", "Enter the exact date")
                    return cleaned_data
                elif is_the_date_accurate == IsTheDateAccurateChoices.approximate and not when_did_you_first_suspected:
                    self.add_error("when_did_you_first_suspect", "Enter the approximate date")
                    return cleaned_data

        return cleaned_data

    def clean_when_did_you_first_suspect(self) -> str | None:
        when_did_you_first_suspect = self.cleaned_data["when_did_you_first_suspect"]
        if when_did_you_first_suspect:
            if when_did_you_first_suspect >= now().date():
                raise forms.ValidationError("The date you first suspected the breach must be in the past")
        return when_did_you_first_suspect


class WhichSanctionsRegimeForm(BaseForm):
    which_sanctions_regime = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=(()),
        required=True,
        error_messages={
            "required": "Select the sanctions regime you suspect has been breached",
            "invalid": "Select the sanctions regime you suspect has been breached or select I do not know",
        },
    )

    class Media:
        js = ["report_a_suspected_breach/javascript/which_sanctions_regime.js"]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        checkbox_choices = []
        for i, item in enumerate(SanctionsRegime.objects.values("full_name")):
            if i == len(SanctionsRegime.objects.values("full_name")) - 1:
                checkbox_choices.append(Choice(item["full_name"], item["full_name"], divider="or"))
            else:
                checkbox_choices.append(Choice(item["full_name"], item["full_name"]))

        checkbox_choices.append(Choice("Unknown Regime", "I do not know"))
        checkbox_choices.append(Choice("Other Regime", "Other regime"))
        self.fields["which_sanctions_regime"].choices = checkbox_choices
        self.fields["which_sanctions_regime"].label = False
        self.helper.label_size = None
        self.helper.label_tag = None
        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id("which_sanctions_regime", field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        if which_sanctions_regime := cleaned_data.get("which_sanctions_regime"):
            if ("Unknown Regime" in which_sanctions_regime or "Other Regime" in which_sanctions_regime) and len(
                which_sanctions_regime
            ) >= 2:
                # the user has selected "I do not know" and other regimes, this is an issue.
                # note that the user can select both "I do not know" and "Other Regime"
                self.add_error(
                    "which_sanctions_regime",
                    forms.ValidationError(
                        code="invalid", message=self.fields["which_sanctions_regime"].error_messages["invalid"]
                    ),
                )
        return cleaned_data


class WhatWereTheGoodsForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["what_were_the_goods"]
        labels = {
            "what_were_the_goods": "What were the goods or services, or what was the technological assistance or technology?",
        }
        help_texts = {
            "what_were_the_goods": "Give a short description. For example: accountancy services",
        }
        error_messages = {
            "what_were_the_goods": {
                "required": "Enter a short description of the goods, services, technological assistance or technology"
            },
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["what_were_the_goods"].widget.attrs = {"rows": 5}


class WhereWereTheGoodsSuppliedFromForm(BaseForm):
    labels = {
        "where_were_the_goods_supplied_from": "Where were the goods, services, "
        "technological assistance or technology supplied from?",
    }

    where_were_the_goods_supplied_from = forms.ChoiceField(
        choices=(()),
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select if the goods, services, technological assistance"
            " or technology were supplied from the UK, or from outside the UK"
        },
    )

    def __init__(self, *args: object, address_string: str | None, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        address_choices = []
        if address_string is not None:
            address_choices.append(Choice("same_address", address_string, divider="or"))

        address_choices += [
            Choice("different_uk_address", "The UK"),
            Choice("outside_the_uk", "Outside the UK"),
            Choice("i_do_not_know", "I do not know"),
            Choice("they_have_not_been_supplied", "They have not been supplied yet"),
        ]
        self.fields["where_were_the_goods_supplied_from"].choices = address_choices


class WhereWereTheGoodsMadeAvailableForm(BaseForm):
    where_were_the_goods_made_available_from = forms.ChoiceField(
        choices=(()),
        widget=forms.RadioSelect,
        label="Where were the goods, services, technological assistance or technology made available from?",
        error_messages={
            "required": "Select if the goods, services, technological assistance or "
            "technology were made available from the UK, or from outside the UK"
        },
    )

    def __init__(self, address_string: str | None, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        address_choices = []
        if address_string is not None:
            address_choices.append(Choice("same_address", address_string, divider="or"))

        address_choices += [
            Choice("different_uk_address", "The UK"),
            Choice("outside_the_uk", "Outside the UK"),
            Choice("i_do_not_know", "I do not know"),
        ]
        self.fields["where_were_the_goods_made_available_from"].choices = address_choices


class WhereWereTheGoodsSuppliedToForm(BaseForm):
    where_were_the_goods_supplied_to = forms.ChoiceField(
        choices=(
            Choice("in_the_uk", "The UK"),
            Choice("outside_the_uk", "Outside the UK"),
            Choice("i_do_not_know", "I do not know"),
        ),
        widget=forms.RadioSelect,
        label="Where were the goods, services, technological assistance or technology supplied to?",
        help_text="This is the address of the end-user",
        error_messages={
            "required": "Select if the goods, services, technology or technical"
            " assistance were supplied to the UK, or to outside the UK"
        },
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        if self.request.GET.get("add_another_end_user") == "yes" and self.request.method == "GET":
            # the user is trying to add another end-user, let's pop the "I do not know" option and clear their selection
            self.fields["where_were_the_goods_supplied_to"].choices.pop(-1)
            self.is_bound = False


class WhereWereTheGoodsMadeAvailableToForm(BaseForm):
    where_were_the_goods_made_available_to = forms.ChoiceField(
        choices=(
            Choice("in_the_uk", "The UK"),
            Choice("outside_the_uk", "Outside the UK"),
            Choice("i_do_not_know", "I do not know"),
        ),
        widget=forms.RadioSelect,
        label="Where were the goods, services, technological assistance or technology made available to?",
        help_text="This is the address of the end-user",
        error_messages={
            "required": "Select if the goods, services, technology or technical "
            "assistance were made available to the UK, or to outside the UK"
        },
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        if self.request.GET.get("add_another_end_user") == "yes" and self.request.method == "GET":
            # the user is trying to add another end-user, let's pop the "I do not know" option
            self.fields["where_were_the_goods_made_available_to"].choices.pop(-1)
            self.is_bound = False


class AboutTheEndUserForm(BasePersonBusinessDetailsForm):
    form_h1_header = "About the end-user"
    labels = {
        "name_of_person": "Name of person",
        "name_of_business": "Name of business",
    }
    help_texts = {
        "name_of_business": "If the end-user is a ship, enter the ship's name",
    }
    revalidate_on_done = False

    name_of_person = forms.CharField()
    name_of_business = forms.CharField()
    email = forms.EmailField(
        error_messages={"invalid": "Enter an email address in the correct format, like name@example.com"}, label="Email address"
    )
    additional_contact_details = forms.CharField(
        widget=forms.Textarea,
        label="Additional contact details",
    )

    class Meta(BasePersonBusinessDetailsForm.Meta):
        model = PersonOrCompany
        fields = (
            "website",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "town_or_city",
            "county",
            "postal_code",
        )
        widgets = BasePersonBusinessDetailsForm.Meta.widgets
        labels = BasePersonBusinessDetailsForm.Meta.labels
        error_messages = BasePersonBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # all fields on this form are optional. Except if it's a non-UK user, then we need the country at least
        for _, field in self.fields.items():
            field.required = False

        if not self.is_uk_address:
            self.fields["additional_contact_details"].help_text = (
                "This could be a phone number, or details of a jurisdiction instead of a country"
            )
            self.fields["country"].required = True

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name_of_person", field_width=Fluid.ONE_HALF),
                Field.text("name_of_business", field_width=Fluid.ONE_HALF),
                Field.text("email", field_width=Fluid.ONE_HALF),
                Field.text("website", field_width=Fluid.ONE_HALF),
                legend="Name and digital contact details",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("county", field_width=Fluid.ONE_THIRD),
                Field.text("postal_code", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Field.textarea("additional_contact_details", field_width=Fluid.FULL, label_tag="h2", label_size=Size.MEDIUM),
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["readable_address"] = get_formatted_address(cleaned_data)
        return cleaned_data


class EndUserAddedForm(BaseForm):
    revalidate_on_done = False

    do_you_want_to_add_another_end_user = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add another end-user?",
        error_messages={"required": "Select yes if you want to add another end-user"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None


class ZeroEndUsersForm(BaseForm):
    revalidate_on_done = False
    form_h1_header = "You've removed all end-users"

    do_you_want_to_add_an_end_user = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add an end-user?",
        error_messages={"required": "Select yes if you want to add an end-user"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None


class WereThereOtherAddressesInTheSupplyChainForm(BaseModelForm):
    hide_optional_label_fields = ["other_addresses_in_the_supply_chain"]

    class Meta:
        model = Breach
        fields = ("were_there_other_addresses_in_the_supply_chain", "other_addresses_in_the_supply_chain")
        labels = {
            "were_there_other_addresses_in_the_supply_chain": "Were there any other addresses in the supply chain?",
            "other_addresses_in_the_supply_chain": "Give all addresses",
        }
        error_messages = {
            "were_there_other_addresses_in_the_supply_chain": {
                "required": "Select yes if there were any other addresses in the supply chain"
            },
            "other_addresses_in_the_supply_chain": {"required": "Enter other addresses in the supply chain"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["were_there_other_addresses_in_the_supply_chain"].empty_label = None
        # todo - abstract the following logic to apply to all ConditionalRadios forms
        self.helper.legend_tag = "h1"
        self.helper.legend_size = Size.LARGE
        self.helper.label_tag = ""
        self.helper.label_size = None
        self.helper.layout = Layout(
            ConditionalRadios(
                "were_there_other_addresses_in_the_supply_chain",
                ConditionalQuestion(
                    "Yes",
                    Field.text("other_addresses_in_the_supply_chain", field_width=Fluid.TWO_THIRDS),
                ),
                "No",
                "I do not know",
            )
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if (
            cleaned_data.get("were_there_other_addresses_in_the_supply_chain") == "yes"
            and not cleaned_data["other_addresses_in_the_supply_chain"]
        ):
            self.add_error(
                "other_addresses_in_the_supply_chain", self.Meta.error_messages["other_addresses_in_the_supply_chain"]["required"]
            )
        return cleaned_data


class UploadDocumentsForm(BaseForm):
    revalidate_on_done = False
    document = MultipleFileField(
        label="Upload a file",
        help_text="Maximum individual file size 100MB. Maximum number of uploads 10",
        required=False,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["document"].widget.attrs["class"] = "govuk-file-upload moj-multi-file-upload__input"
        self.fields["document"].widget.attrs["name"] = "document"
        # redefining this to remove the 'Continue' button from the helper
        self.helper = FormHelper()
        self.helper.layout = Layout("document")

    def clean_document(self) -> list[UploadedDocument]:
        documents = self.cleaned_data.get("document")
        for document in documents:

            # does the document contain a virus?
            try:
                document.readline()
            except VirusFoundInFileException:
                documents.remove(document)
                raise forms.ValidationError(
                    "A virus was found in one of the files you uploaded.",
                )

            # is the document a valid file type?
            mimetype = get_mime_type(document.file)
            valid_mimetype = mimetype in [
                # word documents
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
                # spreadsheets
                "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                # powerpoints
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                # pdf
                "application/pdf",
                # other
                "text/plain",
                "text/csv",
                "application/zip",
                "text/html",
                # images
                "image/jpeg",
                "image/png",
            ]

            _, file_extension = os.path.splitext(document.name)
            valid_extension = file_extension in [
                # word documents
                ".doc",
                ".docx",
                ".odt",
                ".fodt",
                # spreadsheets
                ".xls",
                ".xlsx",
                ".ods",
                ".fods",
                # powerpoints
                ".ppt",
                ".pptx",
                ".odp",
                ".fodp",
                # pdf
                ".pdf",
                # other
                ".txt",
                ".csv",
                ".zip",
                ".html",
                # images
                ".jpeg",
                ".jpg",
                ".png",
            ]

            if not valid_mimetype or not valid_extension:
                raise forms.ValidationError(
                    f"{escape(document.name)} cannot be uploaded, it is not a valid file type", code="invalid_file_type"
                )

            # has the user already uploaded 10 files?
            if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
                if len(session_files) + 1 > 10:
                    raise forms.ValidationError("You can only select up to 10 files at the same time", code="too_many")

            # is the document too large?
            if document.size > 104857600:
                raise forms.ValidationError(f"{document.name} must be smaller than 100 MB", code="too_large")

        return documents


class TellUsAboutTheSuspectedBreachForm(BaseModelForm):

    class Meta:
        model = Breach
        # todo - make all fields variables a tuple
        fields = ["tell_us_about_the_suspected_breach"]
        labels = {
            "tell_us_about_the_suspected_breach": "Give a summary of the breach",
        }
        help_texts = {
            "tell_us_about_the_suspected_breach": "You can also include anything you've not already told us or "
            "uploaded. You could add specific details, such as any "
            "licence numbers or shipping numbers.",
        }
        error_messages = {
            "tell_us_about_the_suspected_breach": {"required": "Enter a summary of the breach"},
        }


class SummaryForm(BaseForm):
    pass


class DeclarationForm(BaseForm):
    declaration = forms.BooleanField(
        label="I agree and accept", required=True, error_messages={"required": "Confirm if you agree and accept the declaration"}
    )
