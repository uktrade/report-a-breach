import logging
from unittest.mock import patch

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from utils.s3 import get_user_uploaded_files

logger = logging.getLogger(__name__)


@patch("report_a_suspected_breach.forms.forms_documents_and_details.get_all_session_files", new=lambda x, y: [])
@patch("report_a_suspected_breach.views.views_documents_and_details.get_all_session_files", new=lambda x, y: [])
class TestDocumentUploadView:
    def test_successful_post(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 201

    def test_file_names_stored_in_cache(self, rasb_client):
        cache.clear()
        assert not get_user_uploaded_files(rasb_client.session)
        rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert get_user_uploaded_files(rasb_client.session) == ["test.png"]

    def test_unsuccessful_post(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("bad.gif", b"GIF8")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        response = response.json()
        assert response["success"] is False
        assert (
            "The selected file must be a DOC, DOCX, ODT, FODT, XLS, XLSX, ODS, FODS, PPT, PPTX, ODP, FODP, "
            "PDF, TXT, CSV, ZIP, HTML, JPEG, JPG or PNG" in response["error"]
        )
        assert response["file_name"] == "bad.gif"
        assert "file_uploads" not in rasb_client.session

    def test_non_ajax_successful_post(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            follow=True,
        )
        assert response.status_code == 200
        assert response.request["PATH_INFO"] == reverse("report_a_suspected_breach:tell_us_about_the_suspected_breach")

    def test_non_ajax_unsuccessful_post(self, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("bad.gif", b"GIF8")},
            follow=True,
        )
        assert response.status_code == 200
        form = response.context["form"]
        assert not form.is_valid()
        assert "govuk-error-summary" in response.content.decode()
        assert (
            "The selected file must be a DOC, DOCX, ODT, FODT, XLS, XLSX, ODS, FODS, PPT, PPTX, ODP, FODP, "
            "PDF, TXT, CSV, ZIP, HTML, JPEG, JPG or PNG" in response.content.decode()
        )


@patch("report_a_suspected_breach.views.views_documents_and_details.TemporaryDocumentStorage.delete")
class TestDeleteDocumentsView:
    def test_successful_post(self, mocked_temporary_document_storage, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_documents") + "?file_name=test.png",
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}
        assert mocked_temporary_document_storage.call_count == 1
        assert mocked_temporary_document_storage.called_with("test.png")

    def test_unsuccessful_post(self, mocked_temporary_document_storage, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_documents"),
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 400
        assert response.json() == {"success": False}
        assert mocked_temporary_document_storage.call_count == 0


class TestDownloadDocumentMiddleman:

    @patch("report_a_suspected_breach.views.views_documents_and_details.get_user_uploaded_files", return_value=["test.png"])
    @patch("report_a_suspected_breach.views.views_documents_and_details.generate_presigned_url", return_value="www.example.com")
    def test_download_document_middleman(self, mocked_uploaded_files, mocked_url, caplog, rasb_client):
        with caplog.at_level(logging.INFO, logger="report_a_suspected_breach.views.views_documents_and_details"):
            session = rasb_client.session
            session.update({"reporter_email_address": "test@example.com"})
            session.save()

            response = rasb_client.get(reverse("report_a_suspected_breach:download_document", kwargs={"file_name": "test.png"}))
            assert "test@example.com has downloaded file: test.png" in caplog.text
        assert response.status_code == 302
        assert response.url == "www.example.com"

    @patch("report_a_suspected_breach.views.views_documents_and_details.get_user_uploaded_files", return_value=["hello.png"])
    def test_download_document_middleman_not_in_cache(self, mocked_uploaded_files, rasb_client):
        response = rasb_client.get(reverse("report_a_suspected_breach:download_document", kwargs={"file_name": "test.png"}))
        assert response.status_code == 404
