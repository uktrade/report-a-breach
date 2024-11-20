from unittest.mock import patch

from django.urls import reverse

from django_app.report_a_suspected_breach import choices
from django_app.report_a_suspected_breach.utils import (
    get_all_cleaned_data,
    get_all_required_fields,
    get_all_required_views,
    get_cleaned_data_for_step,
    get_dirty_form_data,
    get_missing_data,
    get_required_fields,
)


def test_get_dirty_form_data(request_object):
    request_object.session["name"] = "Test Name"
    dirty_data = get_dirty_form_data(request_object, "name")
    session_data = request_object.session["name"]
    assert dirty_data == session_data


def test_get_cleaned_data_for_step(rasb_client, request_object):
    relationship = choices.ReporterProfessionalRelationshipChoices.owner
    rasb_client.post(
        reverse("report_a_suspected_breach:start"),
        data={"reporter_professional_relationship": relationship},
    )
    cleaned_data = get_cleaned_data_for_step(request_object, "start")
    assert cleaned_data["reporter_professional_relationship"] == relationship


def test_get_all_cleaned_data(rasb_client, request_object):
    relationship = choices.ReporterProfessionalRelationshipChoices.owner
    rasb_client.post(
        reverse("report_a_suspected_breach:start"),
        data={"reporter_professional_relationship": relationship},
    )
    rasb_client.post(
        reverse("report_a_suspected_breach:name"),
        data={"reporter_full_name": "Test namee"},
    )
    all_cleaned_data = get_all_cleaned_data(request_object)
    assert all_cleaned_data["start"]["reporter_professional_relationship"] == relationship
    assert all_cleaned_data["name"]["reporter_full_name"] == "Test namee"


def test_get_all_required_views(request_object):
    required_views = get_all_required_views(request_object)
    assert required_views == [
        "start",
        "email",
        "name",
        "are_you_reporting_a_business_on_companies_house",
        "where_is_the_address_of_the_business_or_person",
        "business_or_person_details",
        "when_did_you_first_suspect",
        "which_sanctions_regime",
        "what_were_the_goods",
        "where_were_the_goods_supplied_from",
        "were_there_other_addresses_in_the_supply_chain",
        "tell_us_about_the_suspected_breach",
    ]


@patch("report_a_suspected_breach.form_step_conditions.show_name_and_business_you_work_for_page")
def test_get_all_required_views_name_and_business(mocked_show_name_and_business_you_work_for_page, request_object):
    mocked_show_name_and_business_you_work_for_page.return_value = True
    required_views = get_all_required_views(request_object)
    assert required_views == [
        "start",
        "email",
        "name_and_business_you_work_for",
        "are_you_reporting_a_business_on_companies_house",
        "where_is_the_address_of_the_business_or_person",
        "business_or_person_details",
        "when_did_you_first_suspect",
        "which_sanctions_regime",
        "what_were_the_goods",
        "where_were_the_goods_supplied_from",
        "were_there_other_addresses_in_the_supply_chain",
        "tell_us_about_the_suspected_breach",
    ]


def test_get_all_required_views_business_on_companies_house(request_object):
    request_object.session["are_you_reporting_a_business_on_companies_house"] = {"business_registered_on_companies_house": "yes"}
    request_object.session.save()
    required_views = get_all_required_views(request_object)
    assert required_views == [
        "start",
        "email",
        "name",
        "are_you_reporting_a_business_on_companies_house",
        "do_you_know_the_registered_company_number",
        "when_did_you_first_suspect",
        "which_sanctions_regime",
        "what_were_the_goods",
        "where_were_the_goods_supplied_from",
        "were_there_other_addresses_in_the_supply_chain",
        "tell_us_about_the_suspected_breach",
    ]


def test_get_required_fields(request_object):
    """Get the required fields from the forms."""
    required_fields = get_required_fields(request_object, "name")
    assert required_fields == ["reporter_full_name"]

    required_fields = get_required_fields(request_object, "business_or_person_details")
    assert required_fields == ["name", "country"]


def test_get_all_required_fields(request_object):
    all_required_fields = get_all_required_fields(request_object)
    print(all_required_fields)
    assert all_required_fields == {
        "start": ["reporter_professional_relationship"],
        "email": ["reporter_email_address"],
        "name": ["reporter_full_name"],
        "are_you_reporting_a_business_on_companies_house": ["business_registered_on_companies_house"],
        "where_is_the_address_of_the_business_or_person": ["where_is_the_address"],
        "business_or_person_details": ["name", "country"],
        "when_did_you_first_suspect": ["is_the_date_accurate"],
        "which_sanctions_regime": ["which_sanctions_regime"],
        "what_were_the_goods": ["what_were_the_goods"],
        "where_were_the_goods_supplied_from": ["where_were_the_goods_supplied_from"],
        "were_there_other_addresses_in_the_supply_chain": ["were_there_other_addresses_in_the_supply_chain"],
        "tell_us_about_the_suspected_breach": ["tell_us_about_the_suspected_breach"],
    }


@patch("django_app.report_a_suspected_breach.utils.get_all_cleaned_data")
@patch("django_app.report_a_suspected_breach.utils.get_all_required_fields")
def test_get_no_missing_data(mocked_get_all_required_fields, mocked_get_all_cleaned_data, rasb_client, request_object):
    mocked_get_all_cleaned_data.return_value = {
        "start": {"reporter_professional_relationship": "relationship"},
        "name": {"reporter_full_name": "Test namee"},
        "are_you_reporting_a_business_on_companies_house": {"business_registered_on_companies_house": "no"},
        "when_did_you_first_suspect": {},
    }
    mocked_get_all_required_fields.return_value = {}
    missing_data = get_missing_data(request_object)
    assert missing_data == {}


@patch("django_app.report_a_suspected_breach.utils.get_all_cleaned_data")
@patch("django_app.report_a_suspected_breach.utils.get_all_required_fields")
def test_get_some_missing_data(mocked_get_all_required_fields, mocked_get_all_cleaned_data, rasb_client, request_object):
    mocked_get_all_cleaned_data.return_value = {
        "start": {"reporter_professional_relationship": "relationship"},
        "name": {"reporter_full_name": "Test namee"},
        "are_you_reporting_a_business_on_companies_house": {"business_registered_on_companies_house": "no"},
        "when_did_you_first_suspect": {},
    }

    mocked_get_all_required_fields.return_value = {
        "start": ["reporter_professional_relationship"],
        "name": ["reporter_full_name"],
        "are_you_reporting_a_business_on_companies_house": [
            "business_registered_on_companies_house",
            "registered_company_number",
        ],
        "when_did_you_first_suspect": ["is_the_date_accurate", "when_did_you_first_suspect"],
    }
    missing_data = get_missing_data(request_object)

    assert missing_data == {
        "are_you_reporting_a_business_on_companies_house": {"registered_company_number"},
        "when_did_you_first_suspect": {
            "is_the_date_accurate",
            "when_did_you_first_suspect",
        },
    }
