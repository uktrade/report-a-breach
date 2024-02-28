from crispy_forms_gds.choices import Choice
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    ConditionalQuestion,
    ConditionalRadios,
    Field,
    Layout,
    Submit,
)
from django import forms

import report_a_breach.question_content as content
from report_a_breach.base_classes.forms import BaseForm, BaseModelForm
from report_a_breach.exceptions import CompaniesHouseException
from report_a_breach.utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)

from .models import Breach, SanctionsRegime

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
        widget = forms.TextInput(attrs={"id": "reporter_full_name"})


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

        do_you_know_the_registered_company_number = cleaned_data.get(
            "do_you_know_the_registered_company_number"
        )
        registered_company_number = cleaned_data.get("registered_company_number")
        if do_you_know_the_registered_company_number == "yes":
            if not registered_company_number:
                self.add_error("registered_company_number", "Enter the company number")

            # now we need to get the company details from Companies House
            # and store them in the form. First we check the request session to see if
            # they're already been obtained
            if session_company_details := self.request.session.get("company_details"):
                if (
                    cleaned_data["registered_company_number"]
                    == session_company_details["registered_company_number"]
                ):
                    cleaned_data["registered_company_name"] = session_company_details[
                        "registered_company_name"
                    ]
                    cleaned_data["registered_office_address"] = session_company_details[
                        "registered_office_address"
                    ]
                    return cleaned_data

            try:
                company_details = get_details_from_companies_house(registered_company_number)
                cleaned_data["registered_company_number"] = company_details["company_number"]
                cleaned_data["registered_company_name"] = company_details["company_name"]
                cleaned_data["registered_office_address"] = get_formatted_address(
                    company_details["registered_office_address"]
                )
            except CompaniesHouseException:
                self.add_error(None, "The company number you entered is not valid")

        return cleaned_data


class WhatWereTheGoodsForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["what_were_the_goods"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["what_were_the_goods"].widget.attrs = {"rows": 5}


class WhichSanctionsRegimeForm(BaseForm):
    checkbox_choices = []
    for i, item in enumerate(SanctionsRegime.objects.values("full_name")):
        if i == len(SanctionsRegime.objects.values("full_name")) - 1:
            checkbox_choices.append(Choice(item["full_name"], item["full_name"], divider="or"))
        else:
            checkbox_choices.append(Choice(item["full_name"], item["full_name"]))
    checkbox_choices = tuple(checkbox_choices)
    which_sanctions_regime = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=checkbox_choices,
        label=content.WHICH_SANCTIONS_REGIME["text"],
        required=False,
    )
    unknown_regime = forms.BooleanField(label="I do not know", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field("which_sanctions_regime"),
            Field("unknown_regime"),
        )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("which_sanctions_regime") and not cleaned_data.get(
            "unknown_regime"
        ):
            raise forms.ValidationError(
                "Please select at least one regime or 'I do not know' to continue"
            )
        return cleaned_data


class CheckCompanyDetailsForm(BaseForm):
    pass


class SummaryForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit and Save", css_class="btn-primary"))
