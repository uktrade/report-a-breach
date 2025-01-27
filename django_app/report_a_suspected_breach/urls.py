from django.urls import path
from report_a_suspected_breach.views import (
    generic,
    views_business,
    views_documents_and_details,
    views_end,
    views_sanctions_and_goods,
    views_start,
    views_supply_chain,
)

from django_app.report_a_suspected_breach.views.views_download import DownloadPDFView

app_name = "report_a_suspected_breach"

generic_urls = [
    path("", generic.RedirectBaseReportView.as_view(), name="initial_redirect_view"),
    path("task-list", generic.TaskListView.as_view(), name="tasklist"),
    path("task-list/<str:current_task_name>/", generic.TaskListView.as_view(), name="tasklist_with_current_task"),
]

views_start_urls = [
    path("your-professional-relationship", views_start.StartView.as_view(), name="start"),
    path("your-email-address", views_start.WhatIsYourEmailAddressView.as_view(), name="email"),
    path("enter-security-code", views_start.EmailVerifyView.as_view(), name="verify_email"),
    path("request-new-code", views_start.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("your-details", views_start.NameAndBusinessYouWorkForView.as_view(), name="name_and_business_you_work_for"),
    path("your-name", views_start.YourNameView.as_view(), name="name"),
]

views_business_urls = [
    path(
        "business-registered-with-Companies-House",
        views_business.AreYouReportingCompaniesHouseBusinessView.as_view(),
        name="are_you_reporting_a_business_on_companies_house",
    ),
    path(
        "registered-company-number",
        views_business.DoYouKnowTheRegisteredCompanyNumberView.as_view(),
        name="do_you_know_the_registered_company_number",
    ),
    path("business-location", views_business.ManualCompaniesHouseView.as_view(), name="manual_companies_house_input"),
    path("check-company-details", views_business.CheckCompanyDetailsView.as_view(), name="check_company_details"),
    path(
        "address-of-business-or-person",
        views_business.WhereIsTheAddressOfTheBusinessOrPersonView.as_view(),
        name="where_is_the_address_of_the_business_or_person",
    ),
    path(
        "business-or-person-details/<str:is_uk_address>/",
        views_business.BusinessOrPersonDetailsView.as_view(),
        name="business_or_person_details",
    ),
]

views_sanctions_and_goods_urls = [
    path(
        "date-you-first-suspected-breach",
        views_sanctions_and_goods.WhenDidYouFirstSuspectView.as_view(),
        name="when_did_you_first_suspect",
    ),
    path(
        "sanctions-regime-breached", views_sanctions_and_goods.WhichSanctionsRegimeView.as_view(), name="which_sanctions_regime"
    ),
    path("goods-services-description", views_sanctions_and_goods.WhatWereTheGoodsView.as_view(), name="what_were_the_goods"),
]

views_supply_chain_urls = [
    path(
        "location-where-supplied-from",
        views_supply_chain.WhereWereTheGoodsSuppliedFromView.as_view(),
        name="where_were_the_goods_supplied_from",
    ),
    path("supplier-details/<str:is_uk_address>/", views_supply_chain.AboutTheSupplierView.as_view(), name="about_the_supplier"),
    path(
        "location-where-made-available-from",
        views_supply_chain.WhereWereTheGoodsMadeAvailableFromView.as_view(),
        name="where_were_the_goods_made_available_from",
    ),
    path(
        "location-where-goods-services-made-available-to",
        views_supply_chain.WhereWereTheGoodsMadeAvailableToView.as_view(),
        name="where_were_the_goods_made_available_to",
    ),
    path(
        "location-where-goods-services-made-available-to/<str:end_user_uuid>/",
        views_supply_chain.WhereWereTheGoodsMadeAvailableToView.as_view(),
        name="where_were_the_goods_made_available_to_end_user_uuid",
    ),
    path(
        "location-of-end-user/<str:end_user_uuid>/",
        views_supply_chain.WhereWereTheGoodsSuppliedToView.as_view(),
        name="where_were_the_goods_supplied_to_end_user_uuid",
    ),
    path(
        "location-of-end-user",
        views_supply_chain.WhereWereTheGoodsSuppliedToView.as_view(),
        name="where_were_the_goods_supplied_to",
    ),
    path("end-user-details/<str:end_user_uuid>/", views_supply_chain.AboutTheEndUserView.as_view(), name="about_the_end_user"),
    path("add-end-user", views_supply_chain.EndUserAddedView.as_view(), name="end_user_added"),
    path("delete-end-user", views_supply_chain.DeleteEndUserView.as_view(), name="delete_end_user"),
    path("zero-end-users", views_supply_chain.ZeroEndUsersView.as_view(), name="zero_end_users"),
    path(
        "other-addresses-in-supply-chain",
        views_supply_chain.WereThereOtherAddressesInTheSupplyChainView.as_view(),
        name="were_there_other_addresses_in_the_supply_chain",
    ),
]

views_documents_and_details_urls = [
    path("upload-documents", views_documents_and_details.UploadDocumentsView.as_view(), name="upload_documents"),
    path("delete-documents", views_documents_and_details.DeleteDocumentsView.as_view(), name="delete_documents"),
    path(
        "download-document/<str:file_name>", views_documents_and_details.DownloadDocumentView.as_view(), name="download_document"
    ),
    path(
        "summary-of-breach",
        views_documents_and_details.TellUsAboutTheSuspectedBreachView.as_view(),
        name="tell_us_about_the_suspected_breach",
    ),
]

views_end_urls = [
    path("check-your-answers", views_end.CheckYourAnswersView.as_view(), name="check_your_answers"),
    path("declaration", views_end.DeclarationView.as_view(), name="declaration"),
    path("submission-complete", views_end.CompleteView.as_view(), name="complete"),
    path("download_report/", DownloadPDFView.as_view(), name="download_report"),
]

urlpatterns = (
    generic_urls
    + views_start_urls
    + views_business_urls
    + views_sanctions_and_goods_urls
    + views_supply_chain_urls
    + views_documents_and_details_urls
    + views_end_urls
)

step_to_view_dict = {}
view_to_step_dict = {}

for url in urlpatterns:

    step_to_view_dict[url.name] = url.callback.view_class
    view_to_step_dict[url.callback.view_class.__name__] = url.name
