import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, data, url_paths


class TestWhatWereTheGoods(conftest.PlaywrightTestBase):
    """
    Tests for what were the goods page
    """

    def test_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.create_suspected_data(self.page, exact=True)
        self.create_sanctions(self.page, data.SANCTIONS)
        self.page.get_by_label("What were the goods or").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(
            self.page.get_by_role(
                "link", name="Enter a short description of the goods, services, technological assistance or technology"
            )
        ).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.GOODS_SERVICES_DESCRIPTION}"))

    def test_correct_input_goes_to_where_were_the_goods_supplied_from(self):
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
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.SUPPLY_CHAIN}"))
