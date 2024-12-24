import re

from playwright.sync_api import expect

from tests.test_frontend import conftest


class TestWhichSanctionsRegimes(conftest.PlaywrightTestBase):
    """
    Tests for which sanctions regimes page
    """

    def test_no_input_returns_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.page.get_by_role("heading", name="Which sanctions regimes do").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select the sanctions regime you suspect has been breached")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/sanctions-regime-breached"))

    def test_can_select_multiple_sanctions_regimes(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.page.get_by_role("heading", name="Which sanctions regimes do").click()
        self.page.get_by_label("The Russia (Sanctions) (EU Exit)").check()
        self.page.get_by_label("The Afghanistan").check()
        self.page.get_by_label("The Iran (Sanctions) (Nuclear)").check()
        self.page.get_by_label("The Iran (Sanctions) Regulations").check()
        expect(self.page.get_by_label("The Russia (Sanctions) (EU Exit)")).to_be_checked()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/goods-services-description"))

    def test_i_do_not_know_regime(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.page.get_by_role("heading", name="Which sanctions regimes do").click()
        self.page.get_by_label("The Afghanistan").check()
        self.page.get_by_label("The Iran (Sanctions) (Nuclear)").check()
        self.page.get_by_label("I do not know").check()
        expect(self.page.get_by_label("The Afghanistan")).not_to_be_checked()
        expect(self.page.get_by_label("The Iran (Sanctions) (Nuclear)")).not_to_be_checked()
        expect(self.page.get_by_label("I do not know")).to_be_checked()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/goods-services-description"))
