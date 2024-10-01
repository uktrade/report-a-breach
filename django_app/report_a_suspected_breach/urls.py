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
    path("", generic.RedirectBaseReportView.as_view(), name="initial_redirect_view"),
    path("task-list", generic.TaskListView.as_view(), name="tasklist"),
    path("task-list/<str:current_task_name>/", generic.TaskListView.as_view(), name="tasklist_with_current_task"),
]

views_a_urls = [
    path("your-professional-relationship", views_a.StartView.as_view(), name="start"),
    path("your-email-address", views_a.WhatIsYourEmailAddressView.as_view(), name="email"),
    path("enter-security-code", views_a.EmailVerifyView.as_view(), name="verify_email"),
    path("request-new-code", views_a.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("your-details", views_a.NameAndBusinessYouWorkForView.as_view(), name="name_and_business_you_work_for"),
    path("your-name", views_a.YourNameView.as_view(), name="name"),
]

views_b_urls = [
    path(
        "business-registered-with-Companies-House",
        views_b.AreYouReportingCompaniesHouseBusinessView.as_view(),
        name="are_you_reporting_a_business_on_companies_house",
    ),
    path(
        "registered-company-number",
        views_b.DoYouKnowTheRegisteredCompanyNumberView.as_view(),
        name="do_you_know_the_registered_company_number",
    ),
    path("business-location", views_b.ManualCompaniesHouseView.as_view(), name="manual_companies_house_input"),
    path("check-company-details", views_b.CheckCompanyDetailsView.as_view(), name="check_company_details"),
    path(
        "address-of-business-or-person",
        views_b.WhereIsTheAddressOfTheBusinessOrPersonView.as_view(),
        name="where_is_the_address_of_the_business_or_person",
    ),
    path(
        "business-or-person-details/<str:is_uk_address>/",
        views_b.BusinessOrPersonDetailsView.as_view(),
        name="business_or_person_details",
    ),
]

views_c_urls = [
    path("date-you-first-suspected-breach", views_c.WhenDidYouFirstSuspectView.as_view(), name="when_did_you_first_suspect"),
    path("sanctions-regime-breached", views_c.WhichSanctionsRegimeView.as_view(), name="which_sanctions_regime"),
    path("goods-services-description", views_c.WhatWereTheGoodsView.as_view(), name="what_were_the_goods"),
]

views_d_urls = [
    path(
        "location-where-supplied-from",
        views_d.WhereWereTheGoodsSuppliedFromView.as_view(),
        name="where_were_the_goods_supplied_from",
    ),
    path("supplier-details/<str:is_uk_address>/", views_d.AboutTheSupplierView.as_view(), name="about_the_supplier"),
    path(
        "location-where-made-available-from",
        views_d.WhereWereTheGoodsMadeAvailableFromView.as_view(),
        name="where_were_the_goods_made_available_from",
    ),
    path(
        "location-where-goods-services-made-available-to",
        views_d.WhereWereTheGoodsMadeAvailableToView.as_view(),
        name="where_were_the_goods_made_available_to",
    ),
    path(
        "location-where-goods-services-made-available-to/<str:end_user_uuid>/",
        views_d.WhereWereTheGoodsMadeAvailableToView.as_view(),
        name="where_were_the_goods_made_available_to_end_user_uuid",
    ),
    path(
        "location-of-end-user/<str:end_user_uuid>/",
        views_d.WhereWereTheGoodsSuppliedToView.as_view(),
        name="where_were_the_goods_supplied_to_end_user_uuid",
    ),
    path(
        "location-of-end-user",
        views_d.WhereWereTheGoodsSuppliedToView.as_view(),
        name="where_were_the_goods_supplied_to",
    ),
    path("end-user-details/<str:end_user_uuid>/", views_d.AboutTheEndUserView.as_view(), name="about_the_end_user"),
    path("add-end-user", views_d.EndUserAddedView.as_view(), name="end_user_added"),
    path("delete-end-user", views_d.DeleteEndUserView.as_view(), name="delete_end_user"),
    path("zero-end-users", views_d.ZeroEndUsersView.as_view(), name="zero_end_users"),
    path(
        "other-addresses-in-supply-chain",
        views_d.WereThereOtherAddressesInTheSupplyChainView.as_view(),
        name="were_there_other_addresses_in_the_supply_chain",
    ),
]

views_e_urls = [
    path("upload-documents", views_e.UploadDocumentsView.as_view(), name="upload_documents"),
    path("delete-documents", views_e.DeleteDocumentsView.as_view(), name="delete_documents"),
    path("download-document/<str:file_name>", views_e.DownloadDocumentView.as_view(), name="download_document"),
    path(
        "summary-of-breach",
        views_e.TellUsAboutTheSuspectedBreachView.as_view(),
        name="tell_us_about_the_suspected_breach",
    ),
]

views_f_urls = [
    path("check-your-answers", views_f.CheckYourAnswersView.as_view(), name="check_your_answers"),
    path("declaration", views_f.DeclarationView.as_view(), name="declaration"),
    path("submission-complete", views_f.CompleteView.as_view(), name="complete"),
]

urlpatterns = generic_urls + views_a_urls + views_b_urls + views_c_urls + views_d_urls + views_e_urls + views_f_urls

step_to_view_dict = {}
view_to_step_dict = {}

for url in urlpatterns:

    step_to_view_dict[url.name] = url.callback.view_class
    view_to_step_dict[url.callback.view_class.__name__] = url.name
