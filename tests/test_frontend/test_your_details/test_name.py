import re

from playwright.sync_api import expect

from .. import conftest


class TestNameAndBusinessYouWorkFor(conftest.PlaywrightTestBase):
    """
    Tests for name and business you work for page
    """

    def test_correct_details_goes_to_business_details_page(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Full name").click()
        self.page.get_by_label("Full name").fill("John Smith")
        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Business")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/about_the_person_or_business"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_no_name_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Business")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter your full name")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_no_business_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I work for a third party")
        self.verify_email_details(self.page)
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_label("Full name").click()
        self.page.get_by_label("Full name").fill("John Smith")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business you work for")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/your-details"))
        self.page.get_by_role("link", name="Reset session").click()


class TestName(conftest.PlaywrightTestBase):
    """
    Tests for name page
    """

    def test_correct_details_goes_to_taslkist_page(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I'm an owner, officer or")
        self.verify_email_details(self.page)
        self.page.get_by_text("What is your full name?", exact=True).click()
        self.page.get_by_label("What is your full name?").click()
        self.page.get_by_label("What is your full name?").fill("John Smith")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/about_the_person_or_business"))

    def test_no_name_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "I'm an owner, officer or")
        self.verify_email_details(self.page)
        self.page.get_by_text("What is your full name?", exact=True).click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter your full name")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/your-name"))
