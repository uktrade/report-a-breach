import re

from playwright.sync_api import expect

from .. import conftest


class TestWhereWereTheGoodsSuppliedTo(conftest.PlaywrightTestBase):
    def test_no_input_returns_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_owner_details(self.page)
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where_is_the_address_of_the_business_or_person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role(
            "link",
            name="Select if the address of the business or person suspected of breaching sanctions is in the UK",
        ).click()
        expect(self.page).to_have_url(re.compile(r".*/where_is_the_address_of_the_business_or_person"))

    def test_uk_option_returns_uk_address_capture(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_owner_details(self.page)
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where_is_the_address_of_the_business_or_person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details"))
        expect(self.page.get_by_label("Postcode")).to_be_visible()
        expect(self.page.get_by_label("County (optional)")).to_be_visible()

    def test_non_uk_option_returns_non_uk_address_capture(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_owner_details(self.page)
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where_is_the_address_of_the_business_or_person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details"))
        expect(self.page.get_by_label("Address line 3 (optional)")).to_be_visible()
        expect(self.page.get_by_label("Address line 4 (optional)")).to_be_visible()
        expect(self.page.get_by_label("Country")).to_be_visible()
