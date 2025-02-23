import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths

INCORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "987654"}
EMPTY_CODE_DETAILS = {"email": "test@didigtal.gov.uk", "verify_code": ""}
CORRECT_CODE_DETAILS = {"email": "test@digital.gov.uk", "verify_code": "012345"}


class TestVerify(conftest.PlaywrightTestBase):
    def test_verify_incorrect_code_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.email_details(self.page, INCORRECT_CODE_DETAILS)
        self.verify_email(self.page, INCORRECT_CODE_DETAILS)
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SECURITY_CODE}"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Code is incorrect. Enter the 6 digit")).to_be_visible()

    def test_verify_no_code_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.email_details(self.page, EMPTY_CODE_DETAILS)
        self.verify_email(self.page, EMPTY_CODE_DETAILS)
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SECURITY_CODE}"))
        expect(self.page.get_by_label("There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the 6 digit security code")).to_be_visible()

    def test_verify_code(self):
        self.page.get_by_role("link", name="Your details").click()
        self.reporter_professional_relationship(self.page, "owner")
        self.page.get_by_role("button", name="Continue").click()
        self.email_details(self.page, CORRECT_CODE_DETAILS)
        self.verify_email(self.page, CORRECT_CODE_DETAILS)
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_NAME}"))
