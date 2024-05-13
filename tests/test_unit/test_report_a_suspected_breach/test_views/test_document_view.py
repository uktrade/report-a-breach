from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


@patch("report_a_suspected_breach.views.TemporaryDocumentStorage.save")
@patch("report_a_suspected_breach.forms.get_all_session_files", new=lambda x, y: [])
@patch("report_a_suspected_breach.views.get_all_session_files", new=lambda x, y: [])
class TestDocumentUploadView:
    def test_successful_post(self, mocked_temporary_document_storage, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 201
        assert mocked_temporary_document_storage.call_count == 1
        assert mocked_temporary_document_storage.called_with("file_content", "test.png")
        assert "file_uploads" in rasb_client.session
        assert rasb_client.session["file_uploads"] == ["test.png"]

    def test_unsuccessful_post(self, mocked_temporary_document_storage, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("bad.gif", b"GIF8")},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        response = response.json()
        assert response["success"] is False
        assert "it is not a valid file type" in response["error"]
        assert response["file_name"] == "bad.gif"
        assert "file_uploads" not in rasb_client.session

    def test_non_ajax_successful_post(self, mocked_temporary_document_storage, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("test.png", b"file_content")},
            follow=True,
        )
        assert response.status_code == 200
        assert mocked_temporary_document_storage.call_count == 1
        assert mocked_temporary_document_storage.called_with("file_content", "test.png")
        assert response.resolver_match.kwargs == {"step": "tell_us_about_the_suspected_breach"}

    def test_non_ajax_unsuccessful_post(self, mocked_temporary_document_storage, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:upload_documents"),
            data={"document": SimpleUploadedFile("bad.gif", b"GIF8")},
            follow=True,
        )
        assert response.status_code == 200
        assert mocked_temporary_document_storage.call_count == 0
        form = response.context["form"]
        assert not form.is_valid()
        assert "govuk-error-summary" in response.content.decode()
        assert "it is not a valid file type" in response.content.decode()


@patch("report_a_suspected_breach.views.TemporaryDocumentStorage.delete")
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
