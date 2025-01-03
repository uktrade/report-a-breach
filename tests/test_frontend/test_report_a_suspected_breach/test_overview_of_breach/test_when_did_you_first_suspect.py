import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestWhenDidYouFirstSuspect(conftest.PlaywrightTestBase):
    """
    Tests for when did you first suspect page
    """

    def test_correct_input_returns_sanctions_regime_breached(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.page.get_by_role("heading", name="Date you first suspected the").click()
        self.page.get_by_role("heading", name="Enter the exact date or an").click()
        self.page.get_by_label("Day").click()
        self.page.get_by_label("Day").fill("12")
        self.page.get_by_label("Month").click()
        self.page.get_by_label("Month").fill("12")
        self.page.get_by_label("Year").click()
        self.page.get_by_label("Year").fill("2023")
        self.page.get_by_role("heading", name="Is the date you entered exact").click()
        self.page.get_by_label("Exact date").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SANCTIONS_REGIMES_BREACHED}"))

    def test_future_date_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.page.get_by_role("heading", name="Date you first suspected the").click()
        self.page.get_by_role("heading", name="Enter the exact date or an").click()
        self.page.get_by_label("Day").click()
        self.page.get_by_label("Day").fill("12")
        self.page.get_by_label("Month").click()
        self.page.get_by_label("Month").fill("12")
        self.page.get_by_label("Year").click()
        self.page.get_by_label("Year").fill("3025")
        self.page.get_by_role("heading", name="Is the date you entered exact").click()
        self.page.get_by_label("Exact date").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="The date you first suspected the breach must be in the past")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.DATE_OF_BREACH}"))

    def test_incorrect_date_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.page.get_by_role("heading", name="Date you first suspected the").click()
        self.page.get_by_role("heading", name="Enter the exact date or an").click()
        self.page.get_by_label("Day").click()
        self.page.get_by_label("Day").fill("123")
        self.page.get_by_label("Month").click()
        self.page.get_by_label("Month").fill("12")
        self.page.get_by_label("Year").click()
        self.page.get_by_label("Year").fill("2025")
        self.page.get_by_role("heading", name="Is the date you entered exact").click()
        self.page.get_by_label("Exact date").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="The date you first suspected the breach must be a real date")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.DATE_OF_BREACH}"))

    def test_no_exact_date_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.page.get_by_role("heading", name="Date you first suspected the").click()
        self.page.get_by_role("heading", name="Enter the exact date or an").click()
        self.page.get_by_role("heading", name="Is the date you entered exact").click()
        self.page.get_by_label("Exact date").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the date you first suspected")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.DATE_OF_BREACH}"))

    def test_no_approx_date_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.page.get_by_role("heading", name="Date you first suspected the").click()
        self.page.get_by_role("heading", name="Enter the exact date or an").click()
        self.page.get_by_role("heading", name="Is the date you entered exact").click()
        self.page.get_by_label("Approximate date").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Enter the date you first suspected")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.DATE_OF_BREACH}"))

    def test_no_input_returns_error(self):
        self.page.get_by_role("link", name="Your details").click()
        self.create_reporter_details(self.page, "I'm an owner")
        self.page.get_by_role("link", name="2. About the person or").click()
        self.create_non_uk_breacher(self.page)
        self.page.get_by_role("link", name="Overview of the suspected breach").click()
        self.page.get_by_role("heading", name="Date you first suspected the").click()
        self.page.get_by_role("heading", name="Enter the exact date or an").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select whether the date you entered")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.DATE_OF_BREACH}"))
