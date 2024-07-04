from django.urls import path, re_path

from . import views
from .form_step_conditions import (
    show_about_the_end_user_page,
    show_about_the_supplier_page,
    show_business_or_personal_details_page,
    show_check_company_details_page_condition,
    show_do_you_know_the_registered_company_number_page,
    show_end_user_added_page,
    show_manual_companies_house_input_page,
    show_where_is_the_address_of_the_business_or_person_page_condition,
    show_where_were_the_goods_made_available_from_page,
    show_where_were_the_goods_made_available_to_page,
    show_where_were_the_goods_supplied_to_page,
)
from .views import (
    DeleteDocumentsView,
    DeleteEndUserView,
    DownloadDocumentView,
    NameAndBusinessYouWorkForView,
    UploadDocumentsView,
    ZeroEndUsersView,
)

report_a_suspected_breach_wizard = views.ReportABreachWizardView.as_view(
    url_name="report_a_suspected_breach:step",
    done_step_name="confirmation",
    condition_dict={
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
        "manual_companies_house_input": show_manual_companies_house_input_page,
    },
)

app_name = "report_a_suspected_breach"

urlpatterns = [
    path("", report_a_suspected_breach_wizard, name="landing"),
    path(
        "about_the_end_user/<str:end_user_uuid>/",
        report_a_suspected_breach_wizard,
        name="about_the_end_user",
    ),
    path(
        "where_were_the_goods_supplied_to/<str:end_user_uuid>/",
        report_a_suspected_breach_wizard,
        name="where_were_the_goods_supplied_to",
    ),
    path(
        "where_were_the_goods_made_available_to/<str:end_user_uuid>/",
        report_a_suspected_breach_wizard,
        name="where_were_the_goods_made_available_to",
    ),
    re_path(r"(?P<step>.+)/$", report_a_suspected_breach_wizard, name="step"),
    path("complete", views.CompleteView.as_view(), name="complete"),
    path("upload_documents_view", UploadDocumentsView.as_view(), name="upload_documents"),
    path("delete_documents_view", DeleteDocumentsView.as_view(), name="delete_documents"),
    path("download_document_view/<str:file_name>", DownloadDocumentView.as_view(), name="download_document"),
    path("email_verify", views.EmailVerifyView.as_view(), name="email_verify"),
    path("request_verify_code", views.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("delete_end_user_view", DeleteEndUserView.as_view(), name="delete_end_user"),
    path("zero_end_users", ZeroEndUsersView.as_view(), name="zero_end_users"),
    path("name_and_business_you_work_for", NameAndBusinessYouWorkForView.as_view(), name="name_and_business_you_work_for"),
]
