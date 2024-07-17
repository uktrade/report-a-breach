from django.urls import path
from report_a_suspected_breach.views import generic, views_a, views_b, views_c

app_name = "report_a_suspected_breach"

generic_urls = [
    path("", generic.TaskListView.as_view(), name="tasklist"),
    path("tasklist/<str:current_task_name>/", generic.TaskListView.as_view(), name="tasklist_with_current_task"),
]

views_a_urls = [
    path("start", views_a.StartView.as_view(), name="start"),
    path("email", views_a.WhatIsYourEmailAddressView.as_view(), name="email"),
    path("verify_email", views_a.EmailVerifyView.as_view(), name="verify_email"),
    path(
        "name_and_business_you_work_for", views_a.NameAndBusinessYouWorkForView.as_view(), name="name_and_business_you_work_for"
    ),
    path("name", views_a.YourNameView.as_view(), name="name"),
]

view_b_urls = [
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

view_c_urls = [
    path("when_did_you_first_suspect", views_c.WhenDidYouFirstSuspectView.as_view(), name="when_did_you_first_suspect"),
    path("which_sanctions_regime", views_c.WhichSanctionsRegimeView.as_view(), name="which_sanctions_regime"),
    path("what_were_the_goods", views_c.WhatWereTheGoodsView.as_view(), name="what_were_the_goods"),
]

urlpatterns = generic_urls + views_a_urls + view_b_urls + view_c_urls

step_to_view_dict = {}
view_to_step_dict = {}

for url in urlpatterns:
    step_to_view_dict[url.name] = url.callback.view_class
    view_to_step_dict[url.callback.view_class.__name__] = url.name
