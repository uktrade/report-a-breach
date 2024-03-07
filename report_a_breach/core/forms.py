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
from django_chunk_upload_handlers.clam_av import validate_virus_check_result

import report_a_breach.question_content as content
from report_a_breach.base_classes.forms import BaseForm, BaseModelForm
from report_a_breach.exceptions import CompaniesHouseException
from report_a_breach.utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)

from ..form_fields import BooleanChoiceField
from .models import Breach, PersonOrCompany, SanctionsRegime

# TODO: check the wording of any error messages to match what the UCD team expect


class StartForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_professional_relationship"]
        widgets = {"reporter_professional_relationship": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reporter_professional_relationship"].choices.pop(0)


class EmailForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_email_address"]


class EmailVerifyForm(BaseForm):
    reporter_verify_email = forms.CharField(
        label=f"{content.VERIFY['text']}",
        help_text=f"{content.VERIFY['helper']}",
    )

    def clean_reporter_verify_email(self):
        value = self.cleaned_data["reporter_verify_email"]
        if session_verify_code := self.request.session.get("verify_code"):
            if value != session_verify_code:
                raise forms.ValidationError("The code you entered is incorrect")
        else:
            raise Exception("No verify code in session")

        return value


class NameForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_full_name"]


class NameAndBusinessYouWorkForForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_full_name", "reporter_name_of_business_you_work_for"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reporter_name_of_business_you_work_for"].help_text = (
            "This is the business that employs you, not the business you're reporting"
        )
        self.helper.label_size = None
        self.helper.layout = Layout(
            Fieldset(
                Field.text("reporter_full_name", field_width=Fluid.THREE_QUARTERS),
                Field.text("reporter_name_of_business_you_work_for", field_width=Fluid.THREE_QUARTERS),
                legend="Your details",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
        )


class AreYouReportingABusinessOnCompaniesHouseForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["business_registered_on_companies_house"]
        widgets = {"business_registered_on_companies_house": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["business_registered_on_companies_house"].choices.pop(0)


class DoYouKnowTheRegisteredCompanyNumberForm(BaseModelForm):
    registered_company_name = forms.CharField(required=False)
    registered_office_address = forms.CharField(required=False)

    class Meta:
        model = Breach
        fields = ["do_you_know_the_registered_company_number", "registered_company_number"]
        widgets = {"do_you_know_the_registered_company_number": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["do_you_know_the_registered_company_number"].choices.pop(0)
        self.helper.layout = Layout(
            ConditionalRadios(
                "do_you_know_the_registered_company_number",
                ConditionalQuestion(
                    "Yes",
                    Field.text("registered_company_number"),
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
                self.add_error(None, "The company number you entered is not valid")

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


class BusinessOrPersonDetailsForm(BaseModelForm):
    class Meta:
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

    def __init__(self, *args, is_uk_address=False, **kwargs):
        super().__init__(*args, **kwargs)
        if is_uk_address:
            self.fields["country"].initial = "GB"
            self.fields["country"].widget = forms.HiddenInput()
            del self.fields["address_line_3"]
            del self.fields["address_line_4"]
        else:
            del self.fields["postal_code"]
            del self.fields["county"]
            del self.fields["town_or_city"]

        self.helper.label_size = None
        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.THREE_QUARTERS),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
            Fieldset(
                Field.text("website", field_width=Fluid.THREE_QUARTERS),
                legend="Website",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.ONE_HALF),
                Field.text("address_line_1", field_width=Fluid.ONE_HALF),
                Field.text("address_line_2", field_width=Fluid.ONE_HALF),
                Field.text("address_line_3", field_width=Fluid.ONE_HALF),
                Field.text("address_line_4", field_width=Fluid.ONE_HALF),
                Field.text("town_or_city", field_width=Fluid.ONE_HALF),
                Field.text("county", field_width=Fluid.ONE_HALF),
                Field.text("postal_code", field_width=Fluid.ONE_HALF),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["readable_address"] = get_formatted_address(cleaned_data)
        return cleaned_data

    # todo - merge this form with the AboutTheEndUserForm, or any other address form that changes from UK to non-UK


class WhenDidYouFirstSuspectForm(BaseModelForm):
    class Meta:
        model = PersonOrCompany
        fields = [
            "when_did_you_first_suspect",
        ]
        widgets = {
            "when_did_you_first_suspect": forms.TextInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["when_did_you_first_suspect"].help_text = "You can enter an exact or approximate date"


class WhichSanctionsRegimeForm(BaseForm):
    search_bar = forms.CharField(
        label=content.WHICH_SANCTIONS_REGIME["text"],
        max_length=100,
        required=False,
        help_text=content.WHICH_SANCTIONS_REGIME["helper"][0],
    )
    which_sanctions_regime = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=(()),
        required=False,
        help_text=content.WHICH_SANCTIONS_REGIME["helper"][1],
        label="",  # empty as the question is set in the above search bar
    )
    unknown_regime = forms.BooleanField(label="I do not know", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        checkbox_choices = []
        for i, item in enumerate(SanctionsRegime.objects.values("full_name")):
            if i == len(SanctionsRegime.objects.values("full_name")) - 1:
                checkbox_choices.append(Choice(item["full_name"], item["full_name"], divider="or"))
            else:
                checkbox_choices.append(Choice(item["full_name"], item["full_name"]))
        checkbox_choices = tuple(checkbox_choices)
        self.fields["which_sanctions_regime"].choices = checkbox_choices

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("which_sanctions_regime") and not cleaned_data.get("unknown_regime"):
            raise forms.ValidationError("Please select at least one regime or 'I do not know' to continue")
        return cleaned_data


class WhatWereTheGoodsForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["what_were_the_goods"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["what_were_the_goods"].widget.attrs = {"rows": 5}


class WhereWereTheGoodsSuppliedFromForm(BaseForm):
    where_were_the_goods_supplied_from = forms.ChoiceField(
        choices=(()),
        widget=forms.RadioSelect,
        label="Where were the goods, services, technological assistance or technology supplied from?",
    )

    def __init__(self, *args, address_dict, **kwargs):
        super().__init__(*args, **kwargs)
        address_choices = []
        if address_dict:
            address_string = get_formatted_address(address_dict)
            address_choices.append(Choice("same_address", address_string, divider="Or"))

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
            address_choices.append(Choice("same_address", address_string, divider="Or"))

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
    )


class AboutTheEndUserForm(BaseModelForm):
    name_of_person = forms.CharField(label="Name of person")
    name_of_business = forms.CharField(label="Name of business")
    email = forms.CharField(label="Email")
    additional_contact_details = forms.CharField(
        widget=forms.Textarea,
        help_text="This could be a phone number, or details of a jurisdiction instead of a country",
    )
    readable_address = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
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
        widgets = {
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

    def __init__(self, *args, is_uk_address, **kwargs):
        super().__init__(*args, **kwargs)
        if is_uk_address:
            self.fields["country"].initial = "GB"
            self.fields["country"].widget = forms.HiddenInput()
            del self.fields["address_line_3"]
            del self.fields["address_line_4"]
        else:
            del self.fields["postal_code"]
            del self.fields["county"]
            del self.fields["town_or_city"]

        self.helper.label_size = None
        self.helper.layout = Layout(
            Fieldset(
                Field.text("name_of_person", field_width=Fluid.THREE_QUARTERS),
                Field.text("name_of_business", field_width=Fluid.THREE_QUARTERS),
                Field.text("email", field_width=Fluid.THREE_QUARTERS),
                Field.text("website", field_width=Fluid.THREE_QUARTERS),
                legend="Name and digital contact details",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.ONE_HALF),
                Field.text("address_line_1", field_width=Fluid.ONE_HALF),
                Field.text("address_line_2", field_width=Fluid.ONE_HALF),
                Field.text("address_line_3", field_width=Fluid.ONE_HALF),
                Field.text("address_line_4", field_width=Fluid.ONE_HALF),
                Field.text("town_or_city", field_width=Fluid.ONE_HALF),
                Field.text("county", field_width=Fluid.ONE_HALF),
                Field.text("postal_code", field_width=Fluid.ONE_HALF),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h3",
            ),
            Field.text(
                "additional_contact_details",
                field_width=Fluid.THREE_QUARTERS,
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


class WereThereOtherAddressesInTheSupplyChainForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ("were_there_other_addresses_in_the_supply_chain", "other_addresses_in_the_supply_chain")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["were_there_other_addresses_in_the_supply_chain"].choices.pop(0)
        self.helper.layout = Layout(
            ConditionalRadios(
                "were_there_other_addresses_in_the_supply_chain",
                ConditionalQuestion(
                    "Yes",
                    Field.text("other_addresses_in_the_supply_chain"),
                ),
                "No",
                "I do not know",
            )
        )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tell_us_about_the_suspected_breach"].help_text = (
            "Include anything you've not already told us or uploaded. You could add specific details, "
            "such as any licence numbers or shipping numbers. If you've uploaded your own compliance "
            "investigation, you could give a summary here."
        )


class SummaryForm(BaseForm):
    pass


class DeclarationForm(BaseForm):
    declaration = forms.BooleanField(label="I agree and accept", required=True)
