import re

from playwright.sync_api import expect

from .. import conftest


class TestCheckCompanyDetails(conftest.PlaywrightTestBase):
    """
    Tests for check company details page
    """

    def test_details_match(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("12345678")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/check_company_details"))
        self.page.get_by_role("heading", name="Check company details").click()
        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("12345678").click()
        self.page.get_by_text("Registered company name").click()
        self.page.get_by_text("BOCIOC M LIMITED").click()
        self.page.get_by_text("Registered office address").click()
        self.page.get_by_text("Avocet Close, CV23 0WU").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/when_did_you_first_suspect"))

    def test_can_change_details(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("12345678")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/check_company_details"))
        self.page.get_by_role("heading", name="Check company details").click()
        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("12345678").click()
        self.page.get_by_text("Registered company name").click()
        self.page.get_by_text("BOCIOC M LIMITED").click()
        self.page.get_by_text("Registered office address").click()
        self.page.get_by_text("Avocet Close, CV23 0WU").click()
        self.page.get_by_text("Change").click()
        expect(self.page).to_have_url(re.compile(r".*/do_you_know_the_registered_company_number"))
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("12349876")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/check_company_details"))
        self.page.get_by_role("heading", name="Check company details").click()
        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("12349876").click()
        self.page.get_by_text("Registered company name").click()
        self.page.get_by_text("BISSOT PROPERTY MANAGEMENT LTD").click()
        self.page.get_by_text("Registered office address").click()
        self.page.get_by_text("-22 Wenlock Road, N1 7GU").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/when_did_you_first_suspect"))
