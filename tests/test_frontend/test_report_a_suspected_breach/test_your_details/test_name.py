import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestNameAndBusinessYouWorkFor(conftest.PlaywrightTestBase):
    """
    Tests for name and business you work for page
    """

    def test_correct_details_goes_to_business_details_page(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Full name").click()
        self.page.get_by_label("Full name").fill("John Smith")
        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Business")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.ABOUT_PERSON_OR_BUSINESS}"))

    def test_no_name_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Business")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter your full name")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_DETAILS}"))

    def test_no_business_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Full name").click()
        self.page.get_by_label("Full name").fill("John Smith")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business you work for")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_DETAILS}"))


class TestName(conftest.PlaywrightTestBase):
    """
    Tests for name page
    """

    def test_correct_details_goes_to_taslkist_page(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I'm an owner, officer or")
        self.verify_email_details(self.page)
        self.page.get_by_text("What is your full name?", exact=True).click()
        self.page.get_by_label("What is your full name?").click()
        self.page.get_by_label("What is your full name?").fill("John Smith")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.ABOUT_PERSON_OR_BUSINESS}"))

    def test_no_name_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I'm an owner, officer or")
        self.verify_email_details(self.page)
        self.page.get_by_text("What is your full name?", exact=True).click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter your full name")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_NAME}"))
