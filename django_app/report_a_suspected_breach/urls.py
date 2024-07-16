from django.urls import path
from report_a_suspected_breach.views import generic, views_a, views_e

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

urlpatterns = generic_urls + views_a_urls + views_e_urls

step_to_view_dict = {}
view_to_step_dict = {}

for url in urlpatterns:
    step_to_view_dict[url.name] = url.callback.view_class
    view_to_step_dict[url.callback.view_class.__name__] = url.name
