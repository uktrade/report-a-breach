import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestCheckCompanyDetails(conftest.PlaywrightTestBase):
    """
    Tests for check company details page
    """

    def test_details_match(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("00000001")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_COMPANY_DETAILS}"))
        self.page.get_by_role("heading", name="Check company details").click()
        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("00000001").click()
        self.page.get_by_text("Registered company name").click()
        self.page.get_by_text("Test Company Name").click()
        self.page.get_by_text("Registered office address").click()
        self.page.get_by_text("52 Test St, Test City, CV12 3MD").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.OVERVIEW_OF_BREACH}"))

    def test_can_change_details(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("00000001")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_COMPANY_DETAILS}"))
        self.page.get_by_role("heading", name="Check company details").click()
        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("00000001").click()
        self.page.get_by_text("Registered company name").click()
        self.page.get_by_text("Test Company Name").click()
        self.page.get_by_text("Registered office address").click()
        self.page.get_by_text("52 Test St, Test City, CV12 3MD").click()
        self.page.get_by_text("Change").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.REGISTERED_COMPANY_NUMBER}"))
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("00000002")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_COMPANY_DETAILS}"))
        self.page.get_by_role("heading", name="Check company details").click()
        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("00000002").click()
        self.page.get_by_text("Registered company name").click()
        self.page.get_by_text("Other Company Name").click()
        self.page.get_by_text("Registered office address").click()
        self.page.get_by_text("20-22 Test Road, Test town, EX11 2MD").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.OVERVIEW_OF_BREACH}"))
