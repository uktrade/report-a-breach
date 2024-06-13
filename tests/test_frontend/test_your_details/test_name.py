import re

from playwright.sync_api import expect

from .. import conftest


class TestNameAndBusinessYouWorkFor(conftest.PlaywrightTestBase):
    def test_correct_details_goes_to_taslkist_page(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Full name").click()
        self.page.get_by_label("Full name").fill("John Smith")
        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Business")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/are_you_reporting_a_business_on_companies_house"))

    def test_no_name_raises_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Business")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("There is a problem").click()
        self.page.get_by_role("link", name="Enter your full name").click()
        expect(self.page).to_have_url(re.compile(r".*/name_and_business_you_work_for"))

    def test_no_business_raises_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Full name").click()
        self.page.get_by_label("Full name").fill("John Smith")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("There is a problem").click()
        self.page.get_by_role("link", name="Enter the name of the business you work for").click()
        expect(self.page).to_have_url(re.compile(r".*/name_and_business_you_work_for"))


class TestName(conftest.PlaywrightTestBase):
    def test_correct_details_goes_to_taslkist_page(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I'm an owner, officer or")
        self.verify_email_details(self.page)
        self.page.get_by_text("What is your full name?", exact=True).click()
        self.page.get_by_label("What is your full name?").click()
        self.page.get_by_label("What is your full name?").fill("John Smith")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/are_you_reporting_a_business_on_companies_house"))

    def test_no_name_raises_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I'm an owner, officer or")
        self.verify_email_details(self.page)
        self.page.get_by_text("What is your full name?", exact=True).click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("There is a problem").click()
        self.page.get_by_role("link", name="Enter your full name").click()
        expect(self.page).to_have_url(re.compile(r".*/name"))
