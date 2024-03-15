from . import conftest


class TestVerify(conftest.PlaywrightTestBase):
    def test_user_verify(self):
        self.page.goto("http://localhost:8000/report_a_breach/email/")
        self.page.get_by_label("What is your email address?").click()
        self.page.get_by_label("What is your email address?").fill("tests@digital.gov.uk")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("We've sent you an email").click()
        self.page.get_by_label("We've sent you an email").fill("012345")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_text("Are you reporting a business").click()
