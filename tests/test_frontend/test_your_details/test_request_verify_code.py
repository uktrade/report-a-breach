import re

from playwright.sync_api import expect

from .. import conftest

INCORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "012345"}
EMPTY_CODE_DETAILS = {"email": "test@didigtal.gov.uk", "verify_code": ""}
CORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "987654"}


class TestRequestVerifyCode(conftest.PlaywrightTestBase):
    """
    Test the request verify code page
    """

    def test_contains_contact_details_if_issues(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/request_verify_code")
        self.page.get_by_role("heading", name="Request a new code").click()
        self.page.get_by_text("Still having issues?").click()
        self.page.get_by_text("If you're still having").click()

    def test_request_verify_incorrect_code_raises_error(self):
        self.page.goto(self.get_form_step_page("email"))
        self.email_details(self.page, INCORRECT_CODE_DETAILS)
        self.page.get_by_role("link", name="Not received an email or code").click()
        expect(self.page).to_have_url(re.compile(r".*/request_verify_code"))
        self.page.get_by_role("heading", name="Request a new code").click()
        self.page.get_by_role("button", name="Request a new code").click()
        self.verify_email(self.page, INCORRECT_CODE_DETAILS)
        expect(self.page).to_have_url(re.compile(r".*/email_verify"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Code is incorrect. Enter the 6 digit")).to_be_visible()

    def test_request_verify_no_code_raises_error(self):
        self.page.goto(self.get_form_step_page("email"))
        self.email_details(self.page, EMPTY_CODE_DETAILS)
        self.page.get_by_role("link", name="Not received an email or code").click()
        expect(self.page).to_have_url(re.compile(r".*/request_verify_code"))
        self.page.get_by_role("heading", name="Request a new code").click()
        self.page.get_by_role("button", name="Request a new code").click()
        self.verify_email(self.page, EMPTY_CODE_DETAILS)
        expect(self.page).to_have_url(re.compile(r".*/email_verify"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the 6 digit security code")).to_be_visible()

    def test_correct_request_verify_code(self):
        self.page.goto(self.get_form_step_page("email"))
        self.email_details(self.page, CORRECT_CODE_DETAILS)
        self.page.get_by_role("link", name="Not received an email or code").click()
        expect(self.page).to_have_url(re.compile(r".*/request_verify_code"))
        self.page.get_by_role("heading", name="Request a new code").click()
        self.page.get_by_role("button", name="Request a new code").click()
        self.verify_email(self.page, CORRECT_CODE_DETAILS)
        # returns to tasklist page because previous sections incomplete
        expect(self.page).to_have_url(re.compile(r".*/start"))
