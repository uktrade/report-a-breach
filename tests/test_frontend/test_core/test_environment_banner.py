from django.test import override_settings
from playwright.sync_api import expect

from tests.test_frontend.conftest import PlaywrightTestBase


class TestEnvironmentBanner(PlaywrightTestBase):
    """Tests the non-production banner appears"""

    @override_settings(ENVIRONMENT="production", DEBUG=False)
    def test_banner_does_not_appear_on_production(self):
        self.page.goto(self.base_url)
        expect(self.page.get_by_test_id("environment_banner")).to_be_hidden()

    @override_settings(ENVIRONMENT="production", DEBUG=True)
    def test_banner_does_not_appear_debug_true(self):
        self.page.goto(self.base_url)
        expect(self.page.get_by_test_id("environment_banner")).to_be_hidden()

    @override_settings(ENVIRONMENT="local", DEBUG=True)
    def test_banner_appears(self):
        self.page.goto(self.base_url)
        expect(self.page.get_by_test_id("environment_banner")).to_be_visible()
        expect(self.page.get_by_text("Environment: local")).to_be_visible()

    @override_settings(
        ENVIRONMENT="local", DEBUG=True, CURRENT_BRANCH="test-branch", CURRENT_TAG="v1.0.0", CURRENT_COMMIT="123456"
    )
    def test_banner_content(self):
        self.page.goto(self.base_url)
        expect(self.page.get_by_text("Environment: local")).to_be_visible()
        expect(self.page.get_by_text("Branch: test-branch")).to_be_visible()
        expect(self.page.get_by_text("Tag: v1.0.0")).to_be_visible()
        expect(self.page.get_by_text("Commit: 123456")).to_be_visible()
