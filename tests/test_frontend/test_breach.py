import re

from playwright.sync_api import expect

from . import conftest


class TestChangeBreachDetails(conftest.PlaywrightTestBase):
    def test_can_change_full_name_breach(self):
        self.page = self.create_test_breach()
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
        expect(self.page).to_have_url(re.compile(r".*/name/.*"))
        self.page.get_by_label("What is your full name?").fill("Jane Doe")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        self.page.get_by_role("button", name="Continue").click()
        self.summary_and_declaration_page(self.page)

    def test_can_create_breach(self):
        self.page = self.create_test_breach()
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        self.page.get_by_role("button", name="Continue").click()
        self.summary_and_declaration_page(self.page)
