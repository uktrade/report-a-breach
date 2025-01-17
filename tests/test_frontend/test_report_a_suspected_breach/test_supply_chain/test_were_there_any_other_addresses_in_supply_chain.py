import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestWereThereAnyOtherAddressesInTheSupplyChain(conftest.PlaywrightTestBase):
    """
    Tests for were any other people or businesses involved in the trade page
    """

    def test_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select yes if there were any")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.OTHER_ADDRESSES_SUPPLY_CHAIN}"))

    def test_yes_and_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Give all names and addresses").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter names and addresses of other people")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.OTHER_ADDRESSES_SUPPLY_CHAIN}"))

    def test_yes_and_correct_input_returns_upload_documents(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Give all names and addresses").click()
        self.page.get_by_label("Give all names and addresses").fill("Address 3 in Supply chain")
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.UPLOAD_DOCUMENTS}"))

    def test_no_returns_upload_documents(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.UPLOAD_DOCUMENTS}"))

    def test_i_do_not_know_returns_upload_documents(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. Name and address of the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="People and businesses involved").click()
        self.create_uk_supplier(self.page)
        self.no_end_users(self.page)
        self.page.get_by_role("heading", name="Were any other people or businesses").click()
        self.page.get_by_label("I do not know").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("link", name="Sanctions breach details").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.UPLOAD_DOCUMENTS}"))
