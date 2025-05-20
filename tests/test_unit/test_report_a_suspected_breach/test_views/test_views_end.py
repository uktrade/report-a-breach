import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from report_a_suspected_breach.models import ReporterEmailVerification
from report_a_suspected_breach.views.views_end import (
    CheckYourAnswersView,
    CompleteView,
    DeclarationView,
    DownloadPDFView,
)

from django_app.report_a_suspected_breach.forms.forms_end import DeclarationForm

from . import data


class TestCheckYourAnswersView:
    @patch("report_a_suspected_breach.views.views_end.get_all_cleaned_data")
    def test_get_context_data(self, mocked_get_all_cleaned_data, request_object):
        mocked_get_all_cleaned_data.return_value = data.cleaned_data
        view = CheckYourAnswersView()
        view.setup(request_object)
        context_data = view.get_context_data()
        assert context_data["form_data"] == data.cleaned_data
        assert not context_data["is_third_party_relationship"]

    @patch("report_a_suspected_breach.views.views_end.get_all_cleaned_data")
    @patch("report_a_suspected_breach.views.views_end.get_cleaned_data_for_step")
    @patch("report_a_suspected_breach.views.views_end.show_check_company_details_page_condition")
    def test_get_context_data_with_supplier_same_address(
        self, mock_show_company_details, mock_get_cleaned_data_for_step, mock_get_all_cleaned_data, request_object
    ):
        test_data = {
            "do_you_know_the_registered_company_number": {
                "registered_company_name": "Test Company",
                "readable_address": "1 Test Road",
                "country": "UK",
            },
            "business_or_person_details": {
                "name": "Business Person",
                "readable_address": "456 Business Ave",
                "country": "Business Country",
            },
        }

        mock_get_all_cleaned_data.return_value = test_data
        mock_get_cleaned_data_for_step.return_value = {"where_were_the_goods_supplied_from": "same_address"}
        mock_show_company_details.return_value = True

        view = CheckYourAnswersView()
        view.setup(request_object)
        context_data = view.get_context_data()

        assert context_data["form_data"] == test_data
        assert context_data["form_data"]["about_the_supplier"]["name"] == "Test Company"

        mock_show_company_details.return_value = False

        view = CheckYourAnswersView()
        view.setup(request_object)
        context_data = view.get_context_data()

        assert context_data["form_data"]["about_the_supplier"]["name"] == "Business Person"

    @patch("report_a_suspected_breach.views.views_end.get_all_session_files")
    def test_session_files_are_uploaded(self, mock_get_files, rasb_client):
        mock_get_files.return_value = {"key1": {"file_name": "test.png"}}
        response = rasb_client.get(reverse("report_a_suspected_breach:check_your_answers"))
        assert response.status_code == 200
        mock_get_files.assert_called_once()

        assert "form_data" in response.context
        assert "session_files" in response.context["form_data"]
        assert response.context["form_data"]["session_files"] == {"key1": {"file_name": "test.png"}}

    @patch("report_a_suspected_breach.views.views_end.get_all_cleaned_data")
    def test_end_users_in_session(self, mocked_get_all_cleaned_data, request_object, rasb_client):
        mocked_get_all_cleaned_data.return_value = data.cleaned_data
        request_object.session = rasb_client.session
        request_object.session["end_users"] = ["User 1", "User 2"]
        request_object.session.save()

        view = CheckYourAnswersView()
        view.setup(request_object)
        context_data = view.get_context_data()

        assert "end_users" in context_data["form_data"]
        assert context_data["form_data"]["end_users"] == ["User 1", "User 2"]


class TestDeclarationView:
    @patch("report_a_suspected_breach.models.get_all_cleaned_data")
    def test_form_valid(self, mocked_get_all_cleaned_data, request_object, rasb_client):
        mocked_get_all_cleaned_data.return_value = data.cleaned_data
        request_object.session = rasb_client.session
        request_session = Session.objects.get(session_key=request_object.session.session_key)
        reporter_object = ReporterEmailVerification.objects.create(
            reporter_session=request_session, email_verification_code="012345", verified=True
        )
        reporter_object.save()
        view = DeclarationView()
        view.setup(request_object)
        response = view.form_valid(DeclarationForm(data={}))
        assert response.status_code == 302
        assert response.url == "/report/submission-complete"


class TestCompleteView:
    def test_get_context_data(self, breach_object, rasb_client):
        request_object = RequestFactory().get("/")
        breach_object.save()
        request_object.session = rasb_client.session
        request_object.session["breach_id"] = breach_object.id

        session = rasb_client.session
        breach_object.reporter_session = Session.objects.get(session_key=session.session_key)
        breach_object.save()
        session["breach_id"] = breach_object.id

        view = CompleteView()
        view.setup(request_object)

        response = view.get(request_object)

        # Assert returns success redirect
        expected_response = HttpResponse(status=200, content_type="text/html; charset=utf-8")
        breach = response.context_data["breach"]
        assert breach.id == breach_object.id
        assert response.status_code == expected_response.status_code
        assert response["content-type"] == expected_response["content-type"]

    def test_no_breach_id_redirect(self, rasb_client, breach_object):
        session = rasb_client.session
        session["breach_id"] = str(uuid.uuid4())
        session.save()

        response = rasb_client.get(reverse("report_a_suspected_breach:complete"))
        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:initial_redirect_view")


@pytest.fixture(autouse=True)
def patched_playwright(monkeypatch):
    mock_sync_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_page = MagicMock()

    mock_sync_playwright.return_value.__enter__.return_value = mock_sync_playwright
    mock_sync_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page

    mock_page.pdf.return_value = None
    mock_browser.close.return_value = None

    monkeypatch.setattr("core.base_views.sync_playwright", mock_sync_playwright)

    return mock_sync_playwright, mock_browser, mock_page


class TestDownloadPDFView:
    @patch("report_a_suspected_breach.views.views_end.get_breach_context_data")
    @patch("report_a_suspected_breach.models.Breach.objects.get")
    def test_successful_get(self, mocked_breach_get, mock_get_breach_context_data, patched_playwright, breach_object):
        mock_sync_playwright, mock_browser, mock_page = patched_playwright
        test_reference = "DE1234"

        mocked_breach_get.return_value = breach_object
        mock_get_breach_context_data.return_value = {"test_key": "test_value"}

        request = RequestFactory().get("?reference=" + test_reference)
        request.user = MagicMock()

        view = DownloadPDFView()
        view.setup(request)
        response = view.get(request)

        expected_response = HttpResponse(status=200, content_type="application/pdf")
        assert response.status_code == expected_response.status_code
        assert response["content-type"] == expected_response["content-type"]
        assert response.headers["Content-Disposition"] == "inline; filename=" + f"report-{test_reference}.pdf"

        mock_sync_playwright.chromium.launch.assert_called_once_with(headless=True)
        mock_browser.new_page.assert_called_once()
        mock_page.pdf.assert_called_once_with(
            format="A4", tagged=True, margin={"left": "1.25in", "right": "1.25in", "top": "1in", "bottom": "1in"}
        )
        mock_browser.close.assert_called_once()
