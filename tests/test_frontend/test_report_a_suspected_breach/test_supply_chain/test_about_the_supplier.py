import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, data, url_paths


class TestAboutTheSupplierUKMadeAvailableAddress(conftest.PlaywrightTestBase):
    """
    Tests for about the supplier page on the made-avaiable journey using a UK address
    """

    def test_correct_input_returns_supplied_to(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_uk_made_available_supplier(self.page)
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_MADE_AVAILABLE_TO}"))

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
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("They have not been supplied").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("The UK", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="About the supplier").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business or person")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter address line 1, such as the building and street")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter town or city")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter postcode")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUPPLIER_DETAILS}"))


class TestAboutTheSupplierNonUKMadeAvailableAddress(conftest.PlaywrightTestBase):
    """
    Tests for about the supplier page on the made-avaiable journey using a non-UK address
    """

    def test_correct_input_returns_supplied_to(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_non_uk_made_available_supplier(self.page)
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_MADE_AVAILABLE_TO}"))

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
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("They have not been supplied").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("Outside the UK", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="About the supplier").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business or person")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select country")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUPPLIER_DETAILS}"))


class TestAboutTheSupplierUKAddress(conftest.PlaywrightTestBase):
    """
    Tests for about the supplier page using a UK address
    """

    def test_correct_input_returns_supplied_to(self):
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
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_END_USER}"))

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
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("The UK", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="About the supplier").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business or person")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter address line 1, such as the building and street")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter town or city")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter postcode")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUPPLIER_DETAILS}"))

    def test_incorrect_uk_postcode_returns_error(self):
        supplier_address = data.UK_SUPPLIER_ADDRESS_DETAILS.copy()
        supplier_address["postcode"] = "AA"
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("The UK", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="About the supplier").click()
        self.fill_uk_address_details(self.page, supplier_address)
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter a full UK postcode")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUPPLIER_DETAILS}"))


class TestAboutTheSupplierNonUKAddress(conftest.PlaywrightTestBase):
    """
    Tests for about the supplier page using a non UK address
    """

    def test_correct_input_returns_supplied_to(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.overview_of_breach(self.page)
        self.page.get_by_role("link", name="The supply chain").click()
        self.create_non_uk_supplier(self.page)
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_END_USER}"))

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
        self.page.get_by_role("heading", name="Where were the goods,").click()
        self.page.get_by_label("Outside the UK", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="About the supplier").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business or person")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select country")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUPPLIER_DETAILS}"))
