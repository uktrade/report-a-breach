import re

from playwright.sync_api import expect

from .. import conftest


class TestTellUsAboutTheSuspectedBreach(conftest.PlaywrightTestBase):
    def test_no_input_returns_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
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
        self.upload_documents_page(self.page)
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_text("Give a summary of the breach", exact=True).click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role("link", name="Enter a summary of the breach").click()
        expect(self.page).to_have_url(re.compile(r".*/tell_us_about_the_suspected_breach"))

    def test_correct_input_goes_to_summary(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
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
        self.upload_documents_page(self.page)
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_text("Give a summary of the breach", exact=True).click()
        self.page.get_by_label("Give a summary of the breach").click()
        self.page.get_by_label("Give a summary of the breach").fill("Summary of breach")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary"))
