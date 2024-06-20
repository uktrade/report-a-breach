import re

from playwright.sync_api import expect

from .. import conftest, data


class TestWhichSanctionsRegimes(conftest.PlaywrightTestBase):
    def test_no_input_returns_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.create_sanctions(self.page, data.SANCTIONS)
        self.page.get_by_label("What were the goods or").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role(
            "link", name="Enter a short description of the goods, services, technological assistance or technology"
        ).click()
        expect(self.page).to_have_url(re.compile(r".*/what_were_the_goods"))

    def test_correct_input_goes_to_where_were_the_goods_supplied_from(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.create_sanctions(self.page, data.SANCTIONS)
        self.page.get_by_label("What were the goods or").click()
        self.page.get_by_label("What were the goods or").fill("Description")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where_were_the_goods_supplied_from"))
