import re

from playwright.sync_api import expect

from .. import conftest


class TestReporterProfessionalRelationship(conftest.PlaywrightTestBase):
    """
    Tests for reporter professional relationship page
    """

    def test_reporter_professional_relationship(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        expect(self.page).to_have_url(re.compile(r".*/your-professional-relationship"))
        self.page.get_by_role("heading", name="What is your professional").click()
        self.page.get_by_label("I'm an owner, officer or").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/your-email-address"))
        self.page.get_by_role("link", name="Reset session").click()

    def test_no_relationship_raises_error(self):
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Your details").click()
        expect(self.page).to_have_url(re.compile(r".*/your-professional-relationship"))
        self.page.get_by_role("heading", name="What is your professional").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select your professional")).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/your-professional-relationship"))
        self.page.get_by_role("link", name="Reset session").click()
