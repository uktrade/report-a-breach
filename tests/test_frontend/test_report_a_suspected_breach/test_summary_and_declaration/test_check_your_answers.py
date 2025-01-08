import re

from django.urls import reverse
from playwright.sync_api import expect

from tests.test_frontend import conftest, data, url_paths

breach_details_owner = {
    "reporter_relationship": "I'm an owner",
    "breacher_location": "uk",
    "supplier_location": "uk",
    "exact_date": True,
    "sanctions": ["The Yemen", "The Zimbabwe"],
    "end_users": [],
}

breach_details_third_party = {
    "reporter_relationship": "I work for a third party",
    "breacher_location": "non_uk",
    "supplier_location": "non_uk",
    "exact_date": False,
    "sanctions": ["I do not know"],
}

breach_details_companies_house = {
    "reporter_relationship": "I work for a third party",
    "breacher_location": "companies_house",
    "supplier_location": "uk",
    "exact_date": True,
    "sanctions": ["I do not know"],
}


class TestCheckYourAnswersYourDetails(conftest.PlaywrightTestBase):
    """
    Tests for check your answers page, specific to the your details section
    """

    def test_business_work_for_show_condition(self):
        self.create_breach(self.page, breach_details_third_party)
        self.page.get_by_role("heading", name="Check your answers").click()
        expect(self.page.get_by_text("Person or business you're reporting")).to_be_visible()

    def test_can_change_reporter_full_name(self):
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        self.page.get_by_text("John Smith", exact=True).click()
        self.page.get_by_role("link", name="Change your full name").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_NAME}"))
        self.page.get_by_label("What is your full name?").fill("Jane Doe")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        expect(self.page.get_by_text("Jane Doe")).to_be_visible()
        expect(self.page.get_by_text("John Smith")).not_to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_can_change_name_and_business_reporter_works_for(self):
        self.create_breach(self.page, breach_details_third_party)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        self.page.get_by_text("John Smith", exact=True).click()
        self.page.get_by_role("link", name="Change your full name").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_DETAILS}"))
        self.page.get_by_label("Full name").fill("Jane Doe")
        self.page.get_by_label("Business you work for").fill("Gov")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()

        expect(self.page.get_by_text("Jane Doe")).to_be_visible()
        expect(self.page.get_by_text("John Smith")).not_to_be_visible()
        self.page.get_by_role("link", name="Change business you work for").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.YOUR_DETAILS}"))

        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Reporter Business")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))

        expect(self.page.get_by_text("Reporter Business")).to_be_visible()
        expect(self.page.get_by_text("DBT")).not_to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)


class TestCheckYourAnswersPersonOrBusinessYouAreReporting(conftest.PlaywrightTestBase):
    """
    Tests for check your answers page, specific to the person or business you're reporting section
    """

    def test_can_change_uk_breacher_details(self):
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Person or Business you're reporting").click()
        self.page.get_by_text("Name", exact=True).click()
        # Change name
        self.page.get_by_role("link", name="Change person or business name").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.BUSINESS_OR_PERSON_DETAILS}"))
        self.page.get_by_label("Name of business or person").fill("Breaching Company")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("Breaching Company")).to_be_visible()
        # Change website (remove it)
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(1)
        self.page.get_by_role("link", name="Change person or business website").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.BUSINESS_OR_PERSON_DETAILS}"))
        self.page.get_by_label("Website address (optional)").fill("")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(0)
        # Change address
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("Breach Lane, Breach Avenue, Breach Town, BB00BB, United Kingdom")).to_be_visible()
        self.page.get_by_role("link", name="Change person or business address").click()
        self.page.get_by_label("Town or city").click()
        self.page.get_by_label("Town or city").fill("Another Town")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Breach Lane, Breach Avenue, Another Town, BB00BB, United Kingdom")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_breacher_details_uk_non_uk_url_creation(self):
        """tests that the correct url is created based on the breacher location"""
        self.create_breach(self.page, breach_details_third_party)
        self.page.get_by_role("link", name="Change person or business website").click()
        assert reverse("report_a_suspected_breach:business_or_person_details", kwargs={"is_uk_address": "False"}) in self.page.url

        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_role("link", name="Change person or business website").click()
        assert reverse("report_a_suspected_breach:business_or_person_details", kwargs={"is_uk_address": "True"}) in self.page.url

    def test_can_change_non_uk_breacher_details(self):
        self.create_breach(self.page, breach_details_third_party)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Person or Business you're reporting").click()
        self.page.get_by_text("Name", exact=True).click()
        # Change name
        expect(self.page.get_by_text("German Breacher")).to_be_visible()
        self.page.get_by_role("link", name="Change person or business name").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.BUSINESS_OR_PERSON_DETAILS}"))
        self.page.get_by_label("Name of business or person").fill("Breaching Company")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("Breaching Company")).to_be_visible()
        # Change website (remove it)
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(1)
        self.page.get_by_role("link", name="Change person or business website").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.BUSINESS_OR_PERSON_DETAILS}"))
        self.page.get_by_label("Website address (optional)").fill("")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(0)
        # Change address
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("Germany Lane, Germany Avenue, Germany Town, Germany")).to_be_visible()

        self.page.get_by_role("link", name="Change person or business address").click()
        self.page.get_by_label("Address line 3 (optional)").click()
        self.page.get_by_label("Address line 3 (optional)").fill("Another Line 3")
        self.page.get_by_label("Country").select_option("VE")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Germany Lane, Germany Avenue, Germany Town, Venezuela")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_can_change_companies_house_details(self):
        self.create_breach(self.page, breach_details_companies_house)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Person or business you're").click()
        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("Name", exact=True).click()
        self.page.get_by_text("00000001").click()
        self.page.get_by_text("Test Company Name", exact=True).click()
        self.page.get_by_text("52 Test St, Test City, CV12 3MD, United Kingdom", exact=True).click()
        self.page.get_by_role("link", name="Change registered company").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.REGISTERED_COMPANY_NUMBER}"))

        self.page.get_by_label("Yes").check()
        self.page.get_by_label("Registered company number").click()
        self.page.get_by_label("Registered company number").fill("00000002")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_COMPANY_DETAILS}"))

        self.page.get_by_text("Registered company number", exact=True).click()
        self.page.get_by_text("00000002").click()
        self.page.get_by_text("Registered company name").click()
        self.page.get_by_text("Other Company Name").click()
        self.page.get_by_text("Registered office address").click()
        self.page.get_by_text("20-22 Test Road, Test town, EX11 2MD, United Kingdom").click()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("Registered company number", exact=True)).to_be_visible()
        expect(self.page.get_by_text("00000002")).to_be_visible()
        expect(self.page.get_by_text("00000001")).not_to_be_visible()
        self.page.get_by_text("Other Company Name", exact=True).click()
        self.page.get_by_text("20-22 Test Road, Test town, EX11 2MD, United Kingdom", exact=True).click()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)


class TestCheckYourAnswersOverviewOfTheBreach(conftest.PlaywrightTestBase):
    """
    Tests for check your answers page, specific to the overview of the breach section
    """

    def test_can_change_date_first_suspected_breach(self):
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Overview of the breach").click()
        self.page.get_by_text("When did you first suspect").click()
        expect(self.page.get_by_text("Exact date 03/05/2024")).to_be_visible()
        self.page.get_by_role("link", name="Change when you first").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.DATE_OF_BREACH}"))
        self.page.get_by_role("heading", name="Date you first suspected the").click()
        self.page.get_by_label("Day").fill("1")
        self.page.get_by_label("Month").fill("1")
        self.page.get_by_label("Year").fill("11")
        self.page.get_by_label("Approximate date").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        self.page.get_by_text("When did you first suspect").click()
        expect(self.page.get_by_text("Approximate date 01/01/2011")).to_be_visible()
        expect(self.page.get_by_text("Exact date 03/05/2024")).not_to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_can_change_sanctions_regimes_breached(self):
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_text("Sanctions regimes breached").click()
        expect(self.page.get_by_text("The Yemen")).to_be_visible()
        expect(self.page.get_by_text("The Zimbabwe")).to_be_visible()
        self.page.get_by_role("link", name="Change sanctions regime").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SANCTIONS_REGIMES_BREACHED}"))

        self.page.get_by_label("The Yemen").uncheck()
        self.page.get_by_label("The Zimbabwe").uncheck()
        self.page.get_by_label("The Lebanon").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        self.page.get_by_text("Sanctions regimes breached").click()
        expect(self.page.get_by_text("The Yemen")).not_to_be_visible()
        expect(self.page.get_by_text("The Zimbabwe")).not_to_be_visible()
        expect(self.page.get_by_text("The Lebanon")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_can_change_what_were_the_goods(self):
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_text("What were the goods or").click()
        expect(self.page.get_by_text("Accountancy goods")).to_be_visible()
        self.page.get_by_role("link", name="Change details of the goods").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.GOODS_SERVICES_DESCRIPTION}"))

        self.page.get_by_label("What were the goods or").fill("Technology goods")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("Accountancy goods")).not_to_be_visible()
        expect(self.page.get_by_text("Technology goods")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)


class TestCheckYourAnswersTheSupplyChain(conftest.PlaywrightTestBase):
    """
    Tests for check your answers page, specific to the supply chain section
    """

    def test_can_change_name_and_address_of_supplier_to_unknown(self):
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="The supply chain", exact=True).click()
        self.page.get_by_role("heading", name="Supplier").click()
        self.page.get_by_role("link", name="Change name and address of supplier").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_SUPPLIED_FROM}"))
        self.page.get_by_label("I do not know").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("I do not know")).to_be_visible()
        expect(self.page.get_by_text("Other people or businesses involved in this trade")).to_be_visible()
        expect(self.page.get_by_text("Supply Street, Supply Lane, Supply Town, United Kingdom")).not_to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_can_change_location_of_end_user(self):
        breach = breach_details_owner.copy()
        breach["end_users"] = ["end_user1", "end_user2", "end_user3"]
        self.create_breach(self.page, breach)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="The supply chain", exact=True).click()
        self.page.get_by_role("heading", name="End-user 1").click()
        self.page.get_by_role("heading", name="End-user 2").click()
        self.page.get_by_role("heading", name="End-user 3").click()
        expect(self.page.get_by_text("AL1, AL2, Town")).to_be_visible()

        self.page.get_by_text("End-user 1 Change").get_by_role("link", name="Change").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_END_USER}"))
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.END_USER_DETAILS}"))
        self.page.get_by_label("Country").select_option("AS")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("AL1, AL2, Town", exact=True)).not_to_be_visible()
        expect(self.page.get_by_text("AL1, AL2, Town, American Samoa")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_can_change_name_and_address_of_end_user(self):
        breach = breach_details_owner.copy()
        breach["end_users"] = ["end_user1", "end_user2", "end_user3"]
        self.create_breach(self.page, breach)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="The supply chain", exact=True).click()
        self.page.get_by_role("heading", name="End-user 1").click()
        self.page.get_by_role("heading", name="End-user 2").click()
        self.page.get_by_role("heading", name="End-user 3").click()
        expect(self.page.get_by_text("End User2")).to_be_visible()
        self.page.get_by_text("End-user 2 Change").get_by_role("link", name="Change").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_END_USER}"))
        self.page.get_by_label("Outside the UK").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Name of person (optional)").fill("Alex Good")
        self.page.get_by_label("Country").select_option("AS")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("End User2")).not_to_be_visible()
        expect(self.page.get_by_text("Alex Good")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)

    def test_can_add_another_end_user(self):
        breach = breach_details_owner.copy()
        breach["end_users"] = ["end_user1", "end_user2", "end_user3"]
        self.create_breach(self.page, breach)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="The supply chain", exact=True).click()
        self.page.get_by_role("link", name="Add another end-user end-user").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.LOCATION_END_USER}"))
        self.page = self.create_end_user(self.page, data.END_USERS["end_user4"])
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("End User4")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)


class TestCheckYourAnswersSanctionsBreachDetails(conftest.PlaywrightTestBase):
    """
    Tests for check your answers page, specific to the sanctions breach details section
    """

    def test_can_change_summary_of_the_breach(self):
        self.create_breach(self.page, breach_details_owner)
        self.page.get_by_text("Summary of the breach", exact=True).click()
        expect(self.page.get_by_text("Happened a month ago")).to_be_visible()
        self.page.get_by_role("link", name="Change summary of the breach").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.SUMMARY_OF_BREACH}"))
        self.page.get_by_label("Give a summary of the breach").fill("Occurred last year")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(rf".*/{url_paths.CHECK_YOUR_ANSWERS}"))
        expect(self.page.get_by_text("Happened a month ago")).not_to_be_visible()
        expect(self.page.get_by_text("Occurred last year")).to_be_visible()
        self.page.get_by_role("link", name="Continue").click()
        self.declaration_and_complete_page(self.page)
