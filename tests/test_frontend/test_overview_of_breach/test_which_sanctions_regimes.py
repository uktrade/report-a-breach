import re

from playwright.sync_api import expect

from .. import conftest


class TestWhichSanctionsRegimes(conftest.PlaywrightTestBase):
    def test_no_input_returns_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_owner_details(self.page)
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.page.get_by_role("heading", name="Which sanctions regimes do").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role("link", name="Select the sanctions regime you suspect has been breached").click()
        expect(self.page).to_have_url(re.compile(r".*/which_sanctions_regime"))

    def test_can_select_multiple_sanctions_regimes(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_owner_details(self.page)
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.page.get_by_role("heading", name="Which sanctions regimes do").click()
        self.page.get_by_label("The Oscars").check()
        self.page.get_by_label("Lampshades are us").check()
        expect(self.page.get_by_label("The Oscars")).to_be_checked()
        expect(self.page.get_by_label("The Oscars")).to_be_checked()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/what_were_the_goods"))

    def test_i_do_not_know_regime(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_owner_details(self.page)
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.page.get_by_role("heading", name="Which sanctions regimes do").click()
        self.page.get_by_label("The Oscars").check()
        self.page.get_by_label("Lampshades are us").check()
        self.page.get_by_label("I do not know").check()
        expect(self.page.get_by_label("The Oscars")).not_to_be_checked()
        expect(self.page.get_by_label("The Oscars")).not_to_be_checked()
        expect(self.page.get_by_label("I do not know")).to_be_checked()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/what_were_the_goods"))
