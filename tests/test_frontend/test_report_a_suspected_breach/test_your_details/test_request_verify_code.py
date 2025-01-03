import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths

CORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "012345"}
EMPTY_CODE_DETAILS = {"email": "test@didigtal.gov.uk", "verify_code": ""}
INCORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "987654"}


class TestRequestVerifyCode(conftest.PlaywrightTestBase):
    """
    Test the request verify code page
    """

    def test_contains_contact_details_if_issues(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_label("What is your email address?").fill("test@gmail.com")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Not received an email or code not working").click()
        self.page.get_by_text("Still having issues?").click()
        self.page.get_by_text("If you're still having").click()

    def test_request_verify_incorrect_code_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").fill("test@gmail.com")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="We've sent you an email")
        self.page.get_by_role("link", name="Not received an email or code not working").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.REQUEST_CODE}"))
        self.page.get_by_role("heading", name="Request a new code").click()
        self.page.get_by_role("button", name="Request a new code").click()
        self.page.get_by_role("heading", name="We've sent you an email").click()
        self.page.get_by_label("Enter the 6 digit security").fill(INCORRECT_CODE_DETAILS["verify_code"])
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SECURITY_CODE}"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Code is incorrect. Enter the 6 digit")).to_be_visible()

    def test_request_verify_no_code_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").fill("test@gmail.com")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="We've sent you an email")
        self.page.get_by_role("link", name="Not received an email or code not working").click()
        self.page.get_by_role("button", name="Request a new code").click()
        self.page.get_by_role("heading", name="We've sent you an email").click()
        self.page.get_by_label("Enter the 6 digit security").fill("")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SECURITY_CODE}"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the 6 digit security code")).to_be_visible()

    def test_correct_request_verify_code(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("What is your email address?").fill("test@gmail.com")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="We've sent you an email")
        self.page.get_by_role("link", name="Not received an email or code not working").click()
        self.page.get_by_role("button", name="Request a new code").click()
        self.page.get_by_role("heading", name="We've sent you an email").click()
        self.page.get_by_label("Enter the 6 digit security").fill(CORRECT_CODE_DETAILS["verify_code"])
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_NAME}"))
