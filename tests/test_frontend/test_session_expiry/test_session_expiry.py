import re

from playwright.sync_api import expect

from .. import conftest


class TestUploadDocuments(conftest.PlaywrightTestBase):
    """
    Tests for the upload documents page
    """

    def test_no_input_goes_to_suspected_breach(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were there any other").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_text("Give all addresses").click()
        self.page.get_by_label("Give all addresses").fill("Addr supply chain")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        self.page.get_by_role("heading", name="Upload documents (optional)").click()
        self.page.get_by_text("You can upload items such as").click()
        self.page.get_by_text("Drag and drop files here or").click()
        self.page.get_by_text("Choose files").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary-of-breach"))
