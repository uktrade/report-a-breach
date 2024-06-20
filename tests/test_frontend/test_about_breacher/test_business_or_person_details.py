import re

from playwright.sync_api import expect

from .. import conftest, data


class TestAboutTheSupplierUKAddress(conftest.PlaywrightTestBase):
    def test_correct_input_returns_supplied_to(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        expect(self.page).to_have_url(re.compile(r".*/when_did_you_first_suspect"))

    def test_no_input_returns_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
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
        self.page.get_by_role("heading", name="Business or person details").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role("link", name="Enter the name of the business or person").click()
        self.page.get_by_role("link", name="Enter address line 1, such as the building and street").click()
        self.page.get_by_role("link", name="Enter town or city").click()
        self.page.get_by_role("link", name="Enter postcode").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details"))

    def test_incorrect_uk_postcode_returns_error(self):
        breacher_address = data.UK_BREACHER_ADDRESS_DETAILS
        breacher_address["postcode"] = "AA"
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where_is_the_address_of_the_business_or_person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details"))
        self.fill_uk_address_details(self.page, breacher_address)
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role("link", name="Enter a full UK postcode").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details"))


class TestAboutTheSupplierNonUKAddress(conftest.PlaywrightTestBase):
    def test_correct_input_returns_supplied_to(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        expect(self.page).to_have_url(re.compile(r".*/when_did_you_first_suspect"))

    def test_no_input_returns_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Reset session").click()
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/where_is_the_address_of_the_business_or_person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details"))
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role("link", name="Enter the name of the business or person").click()
        self.page.get_by_role("link", name="Select country").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details"))
