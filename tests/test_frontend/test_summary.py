import re

from playwright.sync_api import expect

from . import PlaywrightTestBase


class TestSummary(PlaywrightTestBase):
    def test_breach_summary(self):
        self.page.goto(self.get_form_step_page("summary"))
        expect(self.page).to_have_url(re.compile(r".*/summary"))
