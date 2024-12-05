import re

from playwright.sync_api import expect

from .. import conftest


class TestEmail(conftest.PlaywrightTestBase):
    """
    Tests for email page
    """

    def test_correct_email_goes_to_verify_page(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_label("What is your email address?").fill("test@gmail.com")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/enter-security-code"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_no_email_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter your email address")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/your-email-address"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_incorrect_format_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_label("What is your email address?").fill("testemail")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter an email in the correct format")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/your-email-address"))
        self.page.get_by_role("link", name="Reset session").click()
