from typing import Any

from core.forms import BaseForm, BaseModelForm
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
from report_a_suspected_breach.fields import DefaultChoiceField
from report_a_suspected_breach.forms.base_forms import BasePersonBusinessDetailsForm
from report_a_suspected_breach.forms.forms_b import BusinessOrPersonDetailsForm
from report_a_suspected_breach.models import Breach, PersonOrCompany

Field.template = "core/custom_fields/field.html"


class AboutTheSupplierForm(BusinessOrPersonDetailsForm):
    form_h1_header = "About the supplier"

    class Meta(BusinessOrPersonDetailsForm.Meta):
        model = BusinessOrPersonDetailsForm.Meta.model
        fields = BusinessOrPersonDetailsForm.Meta.fields
        labels = BusinessOrPersonDetailsForm.Meta.labels
        widgets = BusinessOrPersonDetailsForm.Meta.widgets


class WhereWereTheGoodsSuppliedFromForm(BaseForm):
    labels = {
        "where_were_the_goods_supplied_from": "Where were the goods, services, "
        "technological assistance or technology supplied from?",
    }

    where_were_the_goods_supplied_from = DefaultChoiceField(
        choices=(()),
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select where the goods, services, technological assistance or technology were supplied from"
        },
        valid_values=["same_address"],
    )

    def __init__(self, *args: object, address_string: str | None = None, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        address_choices = []
        if address_string:
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
            "required": "Select where the goods, services, technological assistance or technology were made available from"
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
        self.end_user_uuid = kwargs.pop("end_user_uuid", None)
        super().__init__(*args, **kwargs)

        if self.request.GET.get("add_another_end_user") == "yes" and self.request.method == "GET":
            # the user is trying to add another end-user, let's pop the "I do not know" option and clear their selection
            self.fields["where_were_the_goods_supplied_to"].choices.pop(-1)
            self.is_bound = False
        if self.end_user_uuid:
            # the user is trying to modify an end-user, pop the "I do not know" option
            self.fields["where_were_the_goods_supplied_to"].choices.pop(-1)


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
        self.end_user_uuid = kwargs.pop("end_user_uuid", None)
        super().__init__(*args, **kwargs)
        if self.request.GET.get("add_another_end_user") == "yes" and self.request.method == "GET":
            # the user is trying to add another end-user, let's pop the "I do not know" option
            self.fields["where_were_the_goods_made_available_to"].choices.pop(-1)
            self.is_bound = False
        if self.end_user_uuid:
            # the user is trying to modify an end-user, pop the "I do not know" option
            self.fields["where_were_the_goods_made_available_to"].choices.pop(-1)


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
                Field.text("name_of_person", field_width=Fluid.TWO_THIRDS),
                Field.text("name_of_business", field_width=Fluid.TWO_THIRDS),
                Field.text("email", field_width=Fluid.TWO_THIRDS),
                Field.text("website", field_width=Fluid.TWO_THIRDS),
                legend="Name and digital contact details",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.ONE_HALF),
                Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_3", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_4", field_width=Fluid.TWO_THIRDS),
                Field.text("town_or_city", field_width=Fluid.ONE_HALF),
                Field.text("county", field_width=Fluid.ONE_HALF),
                Field.text("postal_code", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Field.textarea("additional_contact_details", field_width=Fluid.FULL, label_tag="h2", label_size=Size.MEDIUM),
        )


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

        # we never want to remember the choice to this question
        if self.request.method == "GET":
            self.is_bound = False


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
