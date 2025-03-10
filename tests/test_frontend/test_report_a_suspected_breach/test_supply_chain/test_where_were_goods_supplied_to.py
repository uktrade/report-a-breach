import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestWhereWereTheGoodsSuppliedTo(conftest.PlaywrightTestBase):
    """
    Tests for where were the goods supplied to page
    """

    def test_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(
            self.page.get_by_role(
                "link",
                name="Select if the goods, services, technology or technical assistance were supplied to the UK",
            )
        ).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_END_USER}"))

    def test_uk_option_returns_uk_address_capture(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("The UK", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.END_USER_DETAILS}"))
        expect(self.page.get_by_label("Postcode")).to_be_visible()
        expect(self.page.get_by_label("County (optional)")).to_be_visible()

    def test_non_uk_option_returns_non_uk_address_capture(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.END_USER_DETAILS}"))
        expect(self.page.get_by_label("Address line 3 (optional)")).to_be_visible()
        expect(self.page.get_by_label("Address line 4 (optional)")).to_be_visible()
        expect(self.page.get_by_label("Country")).to_be_visible()

    def test_i_do_not_know_returns_other_addresses_in_supply_chain(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("I do not know").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.OTHER_ADDRESSES_SUPPLY_CHAIN}"))
