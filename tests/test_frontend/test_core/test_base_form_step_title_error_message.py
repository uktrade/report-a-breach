import re

from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestBaseFormStepTitleErrorMessage(PlaywrightTestBase):
    def test_error_in_title(self):
        self.page.goto("http://report-a-suspected-breach:8001/report/task-list")
        self.page.get_by_role("link", name="Your details").click()
        # Clicking through without inputting an email address
        self.page.get_by_role("button", name="Continue").click()

        expect(self.page).to_have_title(re.compile("Error: ", re.IGNORECASE))
