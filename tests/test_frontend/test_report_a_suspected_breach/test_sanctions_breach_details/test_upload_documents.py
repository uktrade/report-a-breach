import re

import pytest
from playwright.sync_api import expect

from tests.test_frontend import conftest, data, url_paths


class TestUploadDocuments(conftest.PlaywrightTestBase):
    """
    Tests for the upload documents page
    """

    def test_no_input_goes_to_suspected_breach(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_text("Give all names and addresses").click()
        self.page.get_by_label("Give all names and addresses").fill("Addr supply chain")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SANCTIONS_DETAILS}"))
        self.page.get_by_role("link", name="Sanctions breach details").click()
        self.page.get_by_role("heading", name="Upload documents (optional)").click()
        self.page.get_by_text("You can upload items such as").click()
        self.page.get_by_text("Drag and drop files here or").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUMMARY_OF_BREACH}"))

    def test_correct_files_goes_to_suspected_breach(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_text("Give all names and addresses").click()
        self.page.get_by_label("Give all names and addresses").fill("Addr supply chain")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        self.upload_documents_page(self.page)
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUMMARY_OF_BREACH}"))

    def test_incorrect_filetype_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_text("Give all names and addresses").click()
        self.page.get_by_label("Give all names and addresses").fill("Addr supply chain")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        self.upload_documents_page(self.page, files=data.MISSING_FILE_TYPE)
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("button", name="Continue")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.UPLOAD_DOCUMENTS}"))

    @pytest.mark.usefixtures("patched_clean_document")
    def test_malware_file_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_text("Give all names and addresses").click()
        self.page.get_by_label("Give all names and addresses").fill("Addr supply chain")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        self.upload_documents_page(self.page, files=data.MALWARE_FILE_TYPE)
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="The selected file contains a virus")).to_be_visible()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("mock_malware_file.txt")).not_to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.UPLOAD_DOCUMENTS}"))
