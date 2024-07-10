from django.urls import path

from . import views
from .views import (
    DeleteDocumentsView,
    DeleteEndUserView,
    DownloadDocumentView,
    EmailView,
    NameAndBusinessYouWorkForView,
    NameView,
    StartView,
    TaskView,
    UploadDocumentsView,
    ZeroEndUsersView,
)

app_name = "report_a_suspected_breach"

urlpatterns = [
    path("", TaskView.as_view(), name="landing"),
    path("start", StartView.as_view(), name="start"),
    path("email", EmailView.as_view(), name="email"),
    path("email_verify", views.EmailVerifyView.as_view(), name="email_verify"),
    path("request_verify_code", views.RequestVerifyCodeView.as_view(), name="request_verify_code"),
    path("name", NameView.as_view(), name="name"),
    path("name_and_business_you_work_for", NameAndBusinessYouWorkForView.as_view(), name="name_and_business_you_work_for"),
    path("complete", views.CompleteView.as_view(), name="complete"),
    path("upload_documents_view", UploadDocumentsView.as_view(), name="upload_documents"),
    path("delete_documents_view", DeleteDocumentsView.as_view(), name="delete_documents"),
    path("download_document_view/<str:file_name>", DownloadDocumentView.as_view(), name="download_document"),
    path("delete_end_user_view", DeleteEndUserView.as_view(), name="delete_end_user"),
    path("zero_end_users", ZeroEndUsersView.as_view(), name="zero_end_users"),
]
