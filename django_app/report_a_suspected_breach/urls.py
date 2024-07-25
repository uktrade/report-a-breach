from django.urls import path
from report_a_suspected_breach.views import (
    generic,
    views_a,
    views_b,
    views_c,
    views_d,
    views_e,
    views_f,
)

app_name = "report_a_suspected_breach"

generic_urls = [
    path("", generic.TaskListView.as_view(), name="tasklist"),
    path("tasklist/<str:current_task_name>/", generic.TaskListView.as_view(), name="tasklist_with_current_task"),
]

views_a_urls = [
    path("start", views_a.StartView.as_view(), name="start"),
    path("email", views_a.WhatIsYourEmailAddressView.as_view(), name="email"),
    path("verify_email", views_a.EmailVerifyView.as_view(), name="verify_email"),
    path("request_verify_code", views_a.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path(
        "name_and_business_you_work_for", views_a.NameAndBusinessYouWorkForView.as_view(), name="name_and_business_you_work_for"
    ),
    path("name", views_a.YourNameView.as_view(), name="name"),
]

views_b_urls = [
    path(
        "are_you_reporting_a_business_on_companies_house",
        views_b.AreYouReportingCompaniesHouseBusinessView.as_view(),
        name="are_you_reporting_a_business_on_companies_house",
    ),
    path(
        "do_you_know_the_registered_company_number",
        views_b.DoYouKnowTheRegisteredCompanyNumberView.as_view(),
        name="do_you_know_the_registered_company_number",
    ),
    path("manual_companies_house_input", views_b.ManualCompaniesHouseView.as_view(), name="manual_companies_house_input"),
    path("check_company_details", views_b.CheckCompanyDetailsView.as_view(), name="check_company_details"),
    path(
        "where_is_the_address_of_the_business_or_person",
        views_b.WhereIsTheAddressOfTheBusinessOrPersonView.as_view(),
        name="where_is_the_address_of_the_business_or_person",
    ),
    path(
        "business_or_person_details/<str:is_uk_address>/",
        views_b.BusinessOrPersonDetailsView.as_view(),
        name="business_or_person_details",
    ),
]

views_c_urls = [
    path("when_did_you_first_suspect", views_c.WhenDidYouFirstSuspectView.as_view(), name="when_did_you_first_suspect"),
    path("which_sanctions_regime", views_c.WhichSanctionsRegimeView.as_view(), name="which_sanctions_regime"),
    path("what_were_the_goods", views_c.WhatWereTheGoodsView.as_view(), name="what_were_the_goods"),
]

views_d_urls = [
    path(
        "where_were_the_goods_supplied_from",
        views_d.WhereWereTheGoodsSuppliedFromView.as_view(),
        name="where_were_the_goods_supplied_from",
    ),
    path("about_the_supplier/<str:is_uk_address>/", views_d.AboutTheSupplierView.as_view(), name="about_the_supplier"),
    path(
        "where_were_the_goods_made_available_from",
        views_d.WhereWereTheGoodsMadeAvailableFromView.as_view(),
        name="where_were_the_goods_made_available_from",
    ),
    path(
        "where_were_the_goods_made_available_to",
        views_d.WhereWereTheGoodsMadeAvailableToView.as_view(),
        name="where_were_the_goods_made_available_to",
    ),
    path(
        "where_were_the_goods_made_available_to/<str:end_user_uuid>/",
        views_d.WhereWereTheGoodsMadeAvailableToView.as_view(),
        name="where_were_the_goods_made_available_to_end_user_uuid",
    ),
    path(
        "where_were_the_goods_supplied_to/<str:end_user_uuid>/",
        views_d.WhereWereTheGoodsSuppliedToView.as_view(),
        name="where_were_the_goods_supplied_to_end_user_uuid",
    ),
    path(
        "where_were_the_goods_supplied_to",
        views_d.WhereWereTheGoodsSuppliedToView.as_view(),
        name="where_were_the_goods_supplied_to",
    ),
    path("about_the_end_user/<str:end_user_uuid>/", views_d.AboutTheEndUserView.as_view(), name="about_the_end_user"),
    path("end_user_added", views_d.EndUserAddedView.as_view(), name="end_user_added"),
    path("delete_end_user_view", views_d.DeleteEndUserView.as_view(), name="delete_end_user"),
    path("zero_end_users", views_d.ZeroEndUsersView.as_view(), name="zero_end_users"),
    path(
        "were_there_other_addresses_in_the_supply_chain",
        views_d.WereThereOtherAddressesInTheSupplyChainView.as_view(),
        name="were_there_other_addresses_in_the_supply_chain",
    ),
]

views_e_urls = [
    path("upload_documents", views_e.UploadDocumentsView.as_view(), name="upload_documents"),
    path("delete_documents", views_e.DeleteDocumentsView.as_view(), name="delete_documents"),
    path("download_document/<str:file_name>", views_e.DownloadDocumentView.as_view(), name="download_document"),
    path(
        "tell_us_about_the_suspected_breach",
        views_e.TellUsAboutTheSuspectedBreachView.as_view(),
        name="tell_us_about_the_suspected_breach",
    ),
]

views_f_urls = [
    path("check_your_answers", views_f.CheckYourAnswersView.as_view(), name="check_your_answers"),
    path("declaration", views_f.DeclarationView.as_view(), name="declaration"),
    path("complete", views_f.CompleteView.as_view(), name="complete"),
]

urlpatterns = generic_urls + views_a_urls + views_b_urls + views_c_urls + views_d_urls + views_e_urls + views_f_urls

step_to_view_dict = {}
view_to_step_dict = {}

for url in urlpatterns:

    step_to_view_dict[url.name] = url.callback.view_class
    view_to_step_dict[url.callback.view_class.__name__] = url.name
