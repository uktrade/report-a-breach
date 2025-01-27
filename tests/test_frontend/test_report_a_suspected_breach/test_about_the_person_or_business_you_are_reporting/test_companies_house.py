import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestAreYouReportingABusinessOnCompaniesHouse(conftest.PlaywrightTestBase):
    """
    Tests for are you reporting a business on companies house page
    """

    def test_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(
            self.page.get_by_role(
                "link", name="Select yes if you are reporting a business which is registered with UK Companies House"
            )
        ).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.REGISTERED_ON_COMPANIES_HOUSE}"))

    def test_select_yes_returns_do_you_know_registered_company_number(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.REGISTERED_COMPANY_NUMBER}"))

    def test_no_returns_business_or_person_details(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.ADDRESS_BUSINESS_OR_PERSON}"))

    def test_i_do_not_know_returns_business_or_person_details(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("I do not know").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("No").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.ADDRESS_BUSINESS_OR_PERSON}"))


class TestDoYouKnowTheRegisteredCompanyNumber(conftest.PlaywrightTestBase):
    """
    Tests for do you know the registered company number page
    """

    def test_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.REGISTERED_COMPANY_NUMBER}"))
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select yes if you know the registered company number")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.REGISTERED_COMPANY_NUMBER}"))

    def test_yes_and_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the registered company number")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.REGISTERED_COMPANY_NUMBER}"))

    def test_yes_and_wrong_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("23")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Number not recognised with Companies House")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.REGISTERED_COMPANY_NUMBER}"))

    def test_yes_and_correct_input_returns_check_company_details(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("00000001")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.CHECK_COMPANY_DETAILS}"))

    def test_no_returns_address_details_page(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="Name and address of the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("Yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="Do you know the registered").click()
        self.page.get_by_label("No").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*{url_paths.ADDRESS_BUSINESS_OR_PERSON}"))
