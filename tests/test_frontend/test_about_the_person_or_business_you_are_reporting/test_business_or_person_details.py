import re

from playwright.sync_api import expect

from .. import conftest, data


class TestAboutThePersonOrBusinessUKAddress(conftest.PlaywrightTestBase):
    """
    Tests for about the person or business page, using UK address
    """

    def test_correct_input_returns_next_step_in_task_list(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_uk_breacher(self.page)
        expect(self.page).to_have_url(re.compile(r".*/overview_of_the_suspected_breach/"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_no_input_returns_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/address-of-business-or-person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/business-or-person-details/True/"))
        expect(self.page.get_by_label("Postcode")).to_be_visible()
        expect(self.page.get_by_label("County (optional)")).to_be_visible()
        self.page.get_by_role("heading", name="Business or person details").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business or person")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter address line 1, such as the building and street")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter town or city")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter postcode")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/business-or-person-details"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_incorrect_uk_postcode_returns_error(self):
        breacher_address = data.UK_BREACHER_ADDRESS_DETAILS.copy()
        breacher_address["postcode"] = "AA"
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/address-of-business-or-person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_label("In the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/business-or-person-details"))
        self.fill_uk_address_details(self.page, breacher_address)
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter a full UK postcode")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/business-or-person-details"))
        self.page.get_by_role("link", name="Reset session").click()


class TestAboutThePersonOrBusinessNonUKAddress(conftest.PlaywrightTestBase):
    """
    Tests for about the person or business page, using non UK address
    """

    def test_correct_input_returns_when_did_you_suspect(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        expect(self.page).to_have_url(re.compile(r".*/overview_of_the_suspected_breach/"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_no_input_returns_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.page.get_by_role("heading", name="Are you reporting a business").click()
        self.page.get_by_label("No", exact=True).check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/address-of-business-or-person"))
        self.page.get_by_role("heading", name="Where is the address").click()
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/business-or-person-details"))
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the name of the business or person")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select country")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/business-or-person-details"))
        self.page.get_by_role("link", name="Reset session").click()
