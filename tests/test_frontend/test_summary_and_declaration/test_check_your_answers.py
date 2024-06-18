import re

from playwright.sync_api import expect

from .. import conftest

breach_details_owner = {
    "reporter_relationship": "I'm an owner",
    "breacher_location": "uk",
    "supplier_location": "uk",
    "exact_date": True,
    "sanctions": ["I do not know"],
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
    def test_business_work_for_show_condition(self):
        self.page = self.create_breach(breach_details_third_party)
        self.page.get_by_role("heading", name="Check your answers").click()
        expect(self.page.get_by_text("Business you work for", exact=True)).to_be_visible()

    def test_business_you_work_for_do_not_show_condition(self):
        self.page = self.create_breach(breach_details_owner)
        expect(self.page.get_by_text("Business you work for", exact=True)).not_to_be_visible()

    def test_can_change_reporter_full_name(self):
        self.page = self.create_breach(breach_details_owner)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
        expect(self.page).to_have_url(re.compile(r".*/name/.*"))
        self.page.get_by_label("What is your full name?").fill("Jane Doe")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        expect(self.page.get_by_text("Jane Doe")).to_be_visible()
        expect(self.page.get_by_text("John smith")).not_to_be_visible()
        self.page.get_by_role("button", name="Continue").click()
        self.summary_and_declaration_page(self.page)

    def test_can_change_name_and_business_reporter_works_for(self):
        self.page = self.create_breach(breach_details_third_party)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()
        self.page.get_by_text("Full name", exact=True).click()
        self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
        expect(self.page).to_have_url(re.compile(r".*/name_and_business_you_work_for/.*"))
        self.page.get_by_label("Full name").fill("Jane Doe")
        self.page.get_by_label("Business you work for").fill("Gov")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Your details").click()

        expect(self.page.get_by_text("Jane Doe")).to_be_visible()
        expect(self.page.get_by_text("John smith")).not_to_be_visible()
        self.page.get_by_role("link", name="Change business you work for").click()
        expect(self.page).to_have_url(re.compile(r".*/name_and_business_you_work_for/.*"))

        self.page.get_by_label("Business you work for").click()
        self.page.get_by_label("Business you work for").fill("Reporter Business")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary"))

        expect(self.page.get_by_text("Reporter Business")).to_be_visible()
        expect(self.page.get_by_text("DBT")).not_to_be_visible()
        self.page.get_by_role("button", name="Continue").click()
        self.summary_and_declaration_page(self.page)


class TestCheckYourAnswersBreacherDetails(conftest.PlaywrightTestBase):

    def test_can_change_uk_breacher_details(self):
        self.page = self.create_breach(breach_details_owner)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Person or Business you're reporting").click()
        self.page.get_by_text("Name", exact=True).click()
        # Change name
        self.page.get_by_role("link", name="Change person or business name").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
        self.page.get_by_label("Name of business or person").fill("Breaching Company")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        expect(self.page.get_by_text("Breaching Company")).to_be_visible()
        # Change website (remove it)
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(1)
        self.page.get_by_role("link", name="Change person or business website").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
        self.page.get_by_label("Website address (optional)").fill("")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(0)
        # Change address
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        expect(self.page.get_by_text("Breach Lane, Breach Avenue, Breach Town, BB0 0BB, United Kingdom")).to_be_visible()
        self.page.get_by_role("link", name="Change  person or business address").click()
        self.page.get_by_label("Town or city").click()
        self.page.get_by_label("Town or city").fill("Another Town")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Breach Lane, Breach Avenue, Another Town, BB0 0BB, United Kingdom")).to_be_visible()
        self.page.get_by_role("button", name="Continue").click()
        self.summary_and_declaration_page(self.page)

    def test_can_change_non_uk_breacher_details(self):
        self.page = self.create_breach(breach_details_third_party)
        self.page.get_by_role("heading", name="Check your answers").click()
        self.page.get_by_role("heading", name="Person or Business you're reporting").click()
        self.page.get_by_text("Name", exact=True).click()
        # Change name
        expect(self.page.get_by_text("German Breacher")).to_be_visible()
        self.page.get_by_role("link", name="Change person or business name").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
        self.page.get_by_label("Name of business or person").fill("Breaching Company")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        expect(self.page.get_by_text("Breaching Company")).to_be_visible()
        # Change website (remove it)
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(1)
        self.page.get_by_role("link", name="Change person or business website").click()
        expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
        self.page.get_by_label("Website address (optional)").fill("")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Website", exact=True)).to_have_count(0)
        # Change address
        expect(self.page).to_have_url(re.compile(r".*/summary"))
        expect(self.page.get_by_text("Germany Lane, Germany Avenue, Germany Town, Germany, Germany")).to_be_visible()

        self.page.get_by_role("link", name="Change person or business address").click()
        self.page.get_by_label("Address line 3 (optional)").click()
        self.page.get_by_label("Address line 3 (optional)").fill("Another Line 3")
        self.page.get_by_label("Country").select_option("VE")
        self.page.get_by_role("button", name="Continue").click()
        expect(self.page.get_by_text("Germany Lane, Germany Avenue, Germany Town, Venezuela, Venezuela")).to_be_visible()
        self.page.get_by_role("button", name="Continue").click()
        self.summary_and_declaration_page(self.page)

    # def test_can_change_companies_house_details(self):
    #     self.page = self.create_test_breach()
    #     self.page.get_by_role("heading", name="Check your answers").click()
    #     self.page.get_by_role("heading", name="Your details").click()
    #     self.page.get_by_text("Full name", exact=True).click()
    #     self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
    #     expect(self.page).to_have_url(re.compile(r".*/name/.*"))
    #     self.page.get_by_label("What is your full name?").fill("Jane Doe")
    #     self.page.get_by_role("button", name="Continue").click()
    #     expect(self.page).to_have_url(re.compile(r".*/summary"))
    #     self.page.get_by_role("heading", name="Check your answers").click()
    #     self.page.get_by_role("heading", name="Your details").click()
    #     self.page.get_by_text("Full name", exact=True).click()
    #     self.page.get_by_role("button", name="Continue").click()
    #     self.summary_and_declaration_page(self.page)


# class TestCheckYourAnswersOverviewOfTheBreach(conftest.PlaywrightTestBase):

#     def test_can_change_date_first_suspected_breach(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)

#     def test_can_change_sanctions_regimes_breached(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)

#     def test_can_change_what_were_the_goods(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)


# class TestCheckYourAnswersTheSupplyChain(conftest.PlaywrightTestBase):
#     def test_can_change_location_of_supplier(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)

#     def test_can_change_name_and_address_of_supplier(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)

#     def test_can_change_location_of_end_user(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)

#     def test_can_change_name_and_address_of_end_user(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)

#     def test_can_add_another_end_user(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)


# class TestCheckYourAnswersTheSupplyChain(conftest.PlaywrightTestBase):
#     def test_can_change_uploaded_documents(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)

#     def test_can_change_summary_of_the_breach(self):
#         self.page = self.create_test_breach()
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name/.*"))
#         self.page.get_by_label("What is your full name?").fill("Jane Doe")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.summary_and_declaration_page(self.page)
