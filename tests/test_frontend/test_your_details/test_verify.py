import re

from playwright.sync_api import expect

from .. import conftest

INCORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "987654"}
EMPTY_CODE_DETAILS = {"email": "test@didigtal.gov.uk", "verify_code": ""}
CORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "012345"}


class TestVerify(conftest.PlaywrightTestBase):
    def test_verify_incorrect_code_raises_error(self):
        self.page.goto(self.get_form_step_page("email"))
        self.verify_email_details(self.page, INCORRECT_CODE_DETAILS)
        expect(self.page).to_have_url(re.compile(r".*/email_verify"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Code is incorrect. Enter the 6 digit")).to_be_visible()

    def test_verify_no_code_raises_error(self):
        self.page.goto(self.get_form_step_page("email"))
        self.verify_email_details(self.page, EMPTY_CODE_DETAILS)
        expect(self.page).to_have_url(re.compile(r".*/email_verify"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the 6 digit security code")).to_be_visible()

    def test_verify_code(self):
        self.page.goto(self.get_form_step_page("email"))
        self.verify_email_details(self.page, CORRECT_CODE_DETAILS)
        # returns to tasklist page because previous sections incomplete
        expect(self.page).to_have_url(re.compile(r".*/start"))
