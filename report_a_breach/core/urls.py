from django.urls import path, re_path

from .form_step_conditions import (
    show_about_the_end_user_page,
    show_about_the_supplier_page,
    show_business_or_personal_details_page,
    show_check_company_details_page_condition,
    show_do_you_know_the_registered_company_number_page,
    show_end_user_added_page,
    show_name_and_business_you_work_for_page,
    show_name_page,
    show_where_is_the_address_of_the_business_or_person_page_condition,
    show_where_were_the_goods_made_available_from_page,
    show_where_were_the_goods_made_available_to_page,
    show_where_were_the_goods_supplied_to_page,
)
from .views import CompleteView, ReportABreachWizardView

report_a_breach_wizard = ReportABreachWizardView.as_view(
    url_name="report_a_breach_step",
    done_step_name="confirmation",
    condition_dict={
        "name": show_name_page,
        "name_and_business_you_work_for": show_name_and_business_you_work_for_page,
        "check_company_details": show_check_company_details_page_condition,
        "business_or_person_details": show_business_or_personal_details_page,
        "where_is_the_address_of_the_business_or_person": show_where_is_the_address_of_the_business_or_person_page_condition,
        "do_you_know_the_registered_company_number": show_do_you_know_the_registered_company_number_page,
        "about_the_supplier": show_about_the_supplier_page,
        "where_were_the_goods_made_available_from": show_where_were_the_goods_made_available_from_page,
        "where_were_the_goods_supplied_to": show_where_were_the_goods_supplied_to_page,
        "about_the_end_user": show_about_the_end_user_page,
        "end_user_added": show_end_user_added_page,
        "where_were_the_goods_made_available_to": show_where_were_the_goods_made_available_to_page,
    },
)

urlpatterns = [
    path("", report_a_breach_wizard, name="report_a_breach"),
    path(
        "report_a_breach/about_the_end_user/<str:end_user_uuid>/",
        report_a_breach_wizard,
        name="report_a_breach_about_the_end_user",
    ),
    re_path(r"report_a_breach/(?P<step>.+)/$", report_a_breach_wizard, name="report_a_breach_step"),
    path("complete", CompleteView.as_view(), name="complete"),
]
