import re

from playwright.sync_api import expect

from tests.test_frontend import conftest, url_paths


class TestReporterProfessionalRelationship(conftest.PlaywrightTestBase):
    """
    Tests for reporter professional relationship page
    """

    def test_reporter_professional_relationship(self):
        self.page.get_by_role("link", name="Your details").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.PROFESSIONAL_RELATIONSHIP}"))
        self.page.get_by_role("heading", name="What is your professional").click()
        self.page.get_by_label("I'm an owner, officer or").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.EMAIL_ADDRESS}"))

    def test_no_relationship_raises_error(self):
        self.page.get_by_role("link", name="Your details").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.PROFESSIONAL_RELATIONSHIP}"))
        self.page.get_by_role("heading", name="What is your professional").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_role("heading", name="There is a problem")).to_be_visible()
        expect(self.page.get_by_role("link", name="Select your professional")).to_be_visible()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.PROFESSIONAL_RELATIONSHIP}"))
