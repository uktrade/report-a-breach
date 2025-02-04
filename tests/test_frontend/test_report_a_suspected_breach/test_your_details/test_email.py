import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestEmail(conftest.PlaywrightTestBase):
    """
    Tests for email page
    """

    def test_correct_email_goes_to_verify_page(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_label("What is your email address?").fill("test@gmail.com")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SECURITY_CODE}"))

    def test_no_email_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter your email address")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.EMAIL_ADDRESS}"))

    def test_incorrect_format_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_label("What is your email address?").fill("testemail")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter an email in the correct format")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.EMAIL_ADDRESS}"))
