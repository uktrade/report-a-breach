from core.sites import SiteName
from django.urls import reverse
from playwright.sync_api import expect

from tests.factories import BreachFactory
from tests.test_frontend.conftest import PlaywrightTestBase


class TestSummaryReports(PlaywrightTestBase):
    def test_list_has_four_pages_when_paginated_by_10(self):

        for i in range(31):
            new_breach = BreachFactory.create()
            new_breach.assign_reference()
            new_breach.save()

        view_site_url = f"http://{SiteName.view_a_suspected_breach}:{self.server_thread.port}"
        self.page.goto(view_site_url + reverse("view_a_suspected_breach:summary_reports"))

        pagination = self.page.locator(".govuk-pagination")
        expect(pagination).to_be_visible()

        # Check that there are 4 pages for the list of 31 items
        pagination_items = self.page.locator(".govuk-pagination__item")
        expect(pagination_items).to_have_count(4)

        # Check that the current page shows the correct number
        current_page = self.page.locator(".govuk-pagination__item--current")
        expect(current_page).to_have_text("1")

        # Check that each page only shows 10 licenses
        license_items = self.page.locator("h3.govuk-heading-s:has-text('View suspected breach report ID:')")
        expect(license_items).to_have_count(10)

        # Go to page 4
        page_4_link = self.page.locator(".govuk-pagination__item a:has-text('4')")
        page_4_link.click()

        # Check that page 4 has 1 item
        license_items = self.page.locator("h3.govuk-heading-s:has-text('View suspected breach report ID:')")
        expect(license_items).to_have_count(1)
