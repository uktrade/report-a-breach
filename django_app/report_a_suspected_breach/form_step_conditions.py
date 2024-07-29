from django.http import HttpRequest

from .utils import get_cleaned_data_for_step


def show_name_and_business_you_work_for_page(request: HttpRequest) -> bool:
    data = get_cleaned_data_for_step(request, "start")
    return data.get("reporter_professional_relationship") in ("third_party", "no_professional_relationship")


def show_check_company_details_page_condition(request: HttpRequest) -> bool:
    do_you_know_the_registered_company_number_cleaned_data = get_cleaned_data_for_step(
        request, "do_you_know_the_registered_company_number"
    )
    are_you_reporting_a_business_on_companies_house_step_cleaned_data = get_cleaned_data_for_step(
        request, "are_you_reporting_a_business_on_companies_house"
    )
    manual_input_data = get_cleaned_data_for_step(request, "manual_companies_house_input")
    if manual_input_data.get("manual_companies_house_input", False):
        return False

    show_page = (
        do_you_know_the_registered_company_number_cleaned_data.get("do_you_know_the_registered_company_number", False) == "yes"
        and do_you_know_the_registered_company_number_cleaned_data.get("registered_company_number", False)
        and are_you_reporting_a_business_on_companies_house_step_cleaned_data.get("business_registered_on_companies_house", False)
        == "yes"
    )

    return show_page


def show_about_the_supplier_page(request: HttpRequest) -> bool:
    cleaned_data = get_cleaned_data_for_step(request, "where_were_the_goods_supplied_from")
    cleaned_data_available = get_cleaned_data_for_step(request, "where_were_the_goods_made_available_from")
    choices = ["different_uk_address", "outside_the_uk"]

    show_page = (
        cleaned_data.get("where_were_the_goods_supplied_from", False) in choices
        or cleaned_data_available.get("where_were_the_goods_made_available_from", False) in choices
    )

    return show_page
