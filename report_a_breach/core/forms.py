from datetime import timedelta

from crispy_forms_gds.choices import Choice
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
from django.utils.timezone import now
from django_chunk_upload_handlers.clam_av import validate_virus_check_result

from report_a_breach.base_classes.forms import (
    BaseForm,
    BaseModelForm,
    BasePersonBusinessDetailsForm,
)
from report_a_breach.exceptions import CompaniesHouseException
from report_a_breach.utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)

from ..form_fields import BooleanChoiceField
from .models import Breach, PersonOrCompany, ReporterEmailVerification, SanctionsRegime

# TODO: check the wording of any error messages to match what the UCD team expect
Field.template = "custom_fields/field.html"


# NonGdsField.template = "custom_fields/field.html"


class StartForm(BaseModelForm):
    show_back_button = False

    class Meta:
        model = Breach
        fields = ["reporter_professional_relationship"]
        widgets = {"reporter_professional_relationship": forms.RadioSelect}
        labels = {
            "reporter_professional_relationship": "What is your professional relationship with "
            "the business or person suspected of breaching sanctions?",
        }

    def __init__(self, *args, **kwargs):
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


class EmailVerifyForm(BaseForm):
    bold_labels = False
    form_h1_header = "We've sent you an email"

    email_verification_code = forms.CharField(
        label="Enter the 6 digit security code",
        error_messages={"required": "Please provide the 6 digit code sent to your email to continue"},
    )

    def clean_email_verification_code(self):
        email_verification_code = self.cleaned_data["email_verification_code"]
        verify_timeout_seconds = settings.EMAIL_VERIFY_TIMEOUT_SECONDS
        verification_objects = ReporterEmailVerification.objects.filter(reporter_session=self.request.session.session_key).latest(
            "date_created"
        )
        verify_code = verification_objects.email_verification_code
        if email_verification_code != verify_code:
            raise forms.ValidationError("The code you entered is incorrect")

        # check if the user has submitted the verify code within the specified timeframe
        allowed_lapse = verification_objects.date_created + timedelta(seconds=verify_timeout_seconds)
        if allowed_lapse < now():
            raise forms.ValidationError("The code you entered is no longer valid. Please verify your email again")

        return email_verification_code


class NameForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_full_name"]
        labels = {
            "reporter_full_name": "What is your full name?",
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

    def __init__(self, *args, **kwargs):
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
            "business_registered_on_companies_house": "Are you reporting a business which is registered with Companies House?"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["business_registered_on_companies_house"].choices.pop(0)


class DoYouKnowTheRegisteredCompanyNumberForm(BaseModelForm):
    hide_optional_label_fields = ["registered_company_number"]

    registered_company_name = forms.CharField(required=False)
    registered_office_address = forms.CharField(required=False)

    class Meta:
        model = Breach
        fields = ["do_you_know_the_registered_company_number", "registered_company_number"]
        widgets = {"do_you_know_the_registered_company_number": forms.RadioSelect}
        labels = {
            "do_you_know_the_registered_company_number": "Do you know the registered company number?",
            "registered_company_number": "Registered company number",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def clean(self):
        cleaned_data = super().clean()

        do_you_know_the_registered_company_number = cleaned_data.get("do_you_know_the_registered_company_number")
        registered_company_number = cleaned_data.get("registered_company_number")
        if do_you_know_the_registered_company_number == "yes":
            if not registered_company_number:
                self.add_error("registered_company_number", "Enter the company number")

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
                self.add_error("registered_company_number", "The company number you entered is not valid")

        return cleaned_data


class WhereIsTheAddressOfTheBusinessOrPersonForm(BaseForm):
    where_is_the_address = forms.ChoiceField(
        label="Where is the address of the business or person who made the suspected breach?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.ONE_HALF),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
            Fieldset(
                Field.text("website", field_width=Fluid.ONE_HALF),
                legend="Website",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
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
    class Meta:
        model = Breach
        fields = [
            "when_did_you_first_suspect",
        ]
        widgets = {
            "when_did_you_first_suspect": forms.TextInput,
        }
        help_texts = {
            "when_did_you_first_suspect": "You can enter an exact or approximate date",
        }
        labels = {
            "when_did_you_first_suspect": "When did you first suspect the business or person had breached trade sanctions?",
        }


class WhichSanctionsRegimeForm(BaseForm):
    form_h1_header = "Which sanctions regimes do you suspect the company or person has breached?"
    search_bar = forms.CharField(
        label="Search regimes",
        max_length=100,
        required=False,
    )
    which_sanctions_regime = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=(()),
        required=True,
        label="Select all that apply",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        checkbox_choices = []
        for i, item in enumerate(SanctionsRegime.objects.values("full_name")):
            if i == len(SanctionsRegime.objects.values("full_name")) - 1:
                checkbox_choices.append(Choice(item["full_name"], item["full_name"], divider="or"))
            else:
                checkbox_choices.append(Choice(item["full_name"], item["full_name"]))

        checkbox_choices.append(Choice("don't know", "I don't know"))
        checkbox_choices.append(Choice("other_regime", "Other regime"))
        self.fields["which_sanctions_regime"].choices = checkbox_choices

        self.helper.layout = Layout(
            Field.text("search_bar", field_width=Fluid.THREE_QUARTERS),
            Field.checkboxes("which_sanctions_regime"),
        )
        self.helper.label_size = None
        self.helper.label_tag = None


class WhatWereTheGoodsForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["what_were_the_goods"]
        labels = {
            "what_were_the_goods": "What were the goods or services, or what was the technological assistance or technology?",
        }

    def __init__(self, *args, **kwargs):
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
    )

    def __init__(self, *args, address_string, **kwargs):
        super().__init__(*args, **kwargs)
        address_choices = []
        if address_string:
            address_choices.append(Choice("same_address", address_string, divider="or"))

        address_choices += [
            Choice("different_uk_address", "A different UK address"),
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
    )

    def __init__(self, *args, address_dict, **kwargs):
        super().__init__(*args, **kwargs)
        address_choices = []
        if address_dict:
            address_string = get_formatted_address(address_dict)
            address_choices.append(Choice("same_address", address_string, divider="or"))

        address_choices += [
            Choice("different_uk_address", "A different UK address"),
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
        help_text="This is the adresss of the end-user",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.request.GET.get("add_another_end_user") == "yes":
            # the user is trying to add another end-user, let's pop the "I do not know" option
            self.fields["where_were_the_goods_supplied_to"].choices.pop(-1)


class AboutTheEndUserForm(BasePersonBusinessDetailsForm):
    form_h1_header = "About the end-user"
    labels = {
        "name_of_person": "Name of person",
        "name_of_business": "Name of business",
        "email": "Email address",
    }
    help_texts = {
        "name_of_business": "If the end-user is a ship, enter the ship's name",
    }

    name_of_person = forms.CharField()
    name_of_business = forms.CharField()
    email = forms.CharField()
    additional_contact_details = forms.CharField(
        widget=forms.Textarea,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_uk_address:
            self.fields["additional_contact_details"].help_text = (
                "This could be a phone number, or details of a jurisdiction instead of a country"
            )

        # all fields on this form are optional
        for _, field in self.fields.items():
            field.required = False

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name_of_person", field_width=Fluid.ONE_HALF),
                Field.text("name_of_business", field_width=Fluid.ONE_HALF),
                Field.text("email", field_width=Fluid.ONE_HALF),
                Field.text("website", field_width=Fluid.ONE_HALF),
                legend="Name and digital contact details",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
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
            Field.text(
                "additional_contact_details",
                field_width=Fluid.FULL,
                label_size=Size.MEDIUM,
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["readable_address"] = get_formatted_address(cleaned_data)
        return cleaned_data

    def is_valid(self):
        # todo - we need to set this as True always for now, as the form really only gets validated
        #  with a corresponding end_user_uuid, so we can't validate it here
        #  we need to override render_done() in the WizardView so the resulting form_list
        #  contains all instances of this form for each end_user
        return super().is_valid() or True


class EndUserAddedForm(BaseForm):
    do_you_want_to_add_another_end_user = BooleanChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        widget=forms.RadioSelect,
        label="Do you want to add another end-user?",
    )

    def __init__(self, *args, **kwargs):
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

    def __init__(self, *args, **kwargs):
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

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data["were_there_other_addresses_in_the_supply_chain"] == "yes"
            and not cleaned_data["other_addresses_in_the_supply_chain"]
        ):
            self.add_error("other_addresses_in_the_supply_chain", "required")
        return cleaned_data


class UploadDocumentsForm(BaseForm):
    # todo - add a custom crispy forms widget to make it render like the prototype
    documents = forms.FileField(
        label="Upload documents (optional)",
        help_text="You can upload items such as your own compliance investigation report, "
        "commercial invoices, terms of appointment or other contractual documents.",
        required=False,
        validators=[
            validate_virus_check_result,
        ],
    )


class TellUsAboutTheSuspectedBreachForm(BaseModelForm):
    class Meta:
        model = Breach
        # todo - make all fields variables a tuple
        fields = ["tell_us_about_the_suspected_breach"]
        labels = {
            "tell_us_about_the_suspected_breach": "Tell us about the suspected breach",
        }
        help_texts = {
            "tell_us_about_the_suspected_breach": "Include anything you've not already told us or uploaded. "
            "You could add specific details, such as any licence numbers or "
            "shipping numbers. If you've uploaded your own compliance investigation, "
            "you could give a summary here. ",
        }


class SummaryForm(BaseForm):
    pass


class DeclarationForm(BaseForm):
    declaration = forms.BooleanField(label="I agree and accept", required=True)
