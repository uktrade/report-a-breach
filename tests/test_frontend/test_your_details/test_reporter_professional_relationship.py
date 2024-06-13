import re

from playwright.sync_api import expect

from .. import conftest


class TestReporterProfessionalRelationship(conftest.PlaywrightTestBase):
    def test_reporter_professional_relationship(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        expect(self.page).to_have_url(re.compile(r".*/start*"))
        self.page.get_by_role("heading", name="What is your professional").click()
        self.page.get_by_label("I'm an owner, officer or").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/email"))

    def test_no_relationship_raises_error(self):
        self.page.goto("http://report-a-suspected-breach:8000/report_a_suspected_breach/")
        self.page.get_by_role("link", name="Your details").click()
        expect(self.page).to_have_url(re.compile(r".*/start*"))
        self.page.get_by_role("heading", name="What is your professional").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_role("heading", name="There is a problem").click()
        self.page.get_by_role("link", name="Select your professional").click()
        expect(self.page).to_have_url(re.compile(r".*/start*"))
