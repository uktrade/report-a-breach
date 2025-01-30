from unittest.mock import MagicMock

import pytest
from core.base_views import BaseDownloadPDFView
from django.http import HttpResponse
from django.test import RequestFactory

# from django.urls import reverse


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
    def test_successful_get(self, patched_playwright, rasb_client):
        mock_sync_playwright, mock_browser, mock_page = patched_playwright
        test_reference = "DE1234"
        request = RequestFactory().get("?reference=" + test_reference)

        view = BaseDownloadPDFView()
        view.setup(request, reference=test_reference)
        response = view.get(request, reference=test_reference)

        expected_response = HttpResponse(status=200, content_type="application/pdf")
        assert response.status_code == expected_response.status_code
        assert response["content-type"] == expected_response["content-type"]
        assert response.headers["Content-Disposition"] == "inline; filename=" + f"report-{test_reference}.pdf"

        mock_sync_playwright.chromium.launch.assert_called_once_with(headless=True)
        mock_browser.new_page.assert_called_once()
        mock_page.pdf.assert_called_once_with(format="A4")
        mock_browser.close.assert_called_once()
