import re

from playwright.sync_api import expect

from tests.test_frontend import conftest


class TestWereThereAnyOtherAddressesInTheSupplyChain(conftest.PlaywrightTestBase):
    """
    Tests for were there any other addresses in the supply chain page
    """

    def test_no_input_returns_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were there any other").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select yes if there were any")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/other-addresses-in-supply-chain"))

    def test_yes_and_no_input_returns_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were there any other").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Give all addresses").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter other addresses in the supply chain")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/other-addresses-in-supply-chain"))

    def test_yes_and_correct_input_returns_upload_documents(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were there any other").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Give all addresses").click()
        self.page.get_by_label("Give all addresses").fill("Address 3 in Supply chain")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        expect(self.page).to_have_url(re.compile(r".*/upload-documents"))

    def test_no_returns_upload_documents(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were there any other").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        expect(self.page).to_have_url(re.compile(r".*/upload-documents"))

    def test_i_do_not_know_returns_upload_documents(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were there any other").click()
        self.page.get_by_label("I do not know").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        expect(self.page).to_have_url(re.compile(r".*/upload-documents"))
