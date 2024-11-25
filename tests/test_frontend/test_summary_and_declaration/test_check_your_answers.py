# import re
#
# from playwright.sync_api import expect
#
# from .. import conftest, data
#
# breach_details_owner = {
#     "reporter_relationship": "I'm an owner",
#     "breacher_location": "uk",
#     "supplier_location": "uk",
#     "exact_date": True,
#     "sanctions": ["The Oscars", "Fireplaces"],
#     "end_users": [],
# }
#
# breach_details_third_party = {
#     "reporter_relationship": "I work for a third party",
#     "breacher_location": "non_uk",
#     "supplier_location": "non_uk",
#     "exact_date": False,
#     "sanctions": ["I do not know"],
# }
#
# breach_details_companies_house = {
#     "reporter_relationship": "I work for a third party",
#     "breacher_location": "companies_house",
#     "supplier_location": "uk",
#     "exact_date": True,
#     "sanctions": ["I do not know"],
# }
#
#
# class TestCheckYourAnswersYourDetails(conftest.PlaywrightTestBase):
#     """
#     Tests for check your answers page, specific to the your details section
#     """
#
#     def test_business_work_for_show_condition(self):
#         self.page = self.create_breach(breach_details_third_party)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         expect(self.page.get_by_text("Business you work for", exact=True)).to_be_visible()
#
#     def test_business_you_work_for_do_not_show_condition(self):
#         self.page = self.create_breach(breach_details_owner)
#         expect(self.page.get_by_text("Business you work for", exact=True)).not_to_be_visible()
#
#     def test_can_change_reporter_full_name(self):
#         self.page = self.create_breach(breach_details_owner)
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
#         expect(self.page.get_by_text("Jane Doe")).to_be_visible()
#         expect(self.page.get_by_text("John smith")).not_to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_name_and_business_reporter_works_for(self):
#         self.page = self.create_breach(breach_details_third_party)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#         self.page.get_by_text("Full name", exact=True).click()
#         self.page.locator("form div").filter(has_text="Full name John smith Change").get_by_role("link").click()
#         expect(self.page).to_have_url(re.compile(r".*/name_and_business_you_work_for/.*"))
#         self.page.get_by_label("Full name").fill("Jane Doe")
#         self.page.get_by_label("Business you work for").fill("Gov")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Your details").click()
#
#         expect(self.page.get_by_text("Jane Doe")).to_be_visible()
#         expect(self.page.get_by_text("John smith")).not_to_be_visible()
#         self.page.get_by_role("link", name="Change business you work for").click()
#         expect(self.page).to_have_url(re.compile(r".*/name_and_business_you_work_for/.*"))
#
#         self.page.get_by_label("Business you work for").click()
#         self.page.get_by_label("Business you work for").fill("Reporter Business")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#
#         expect(self.page.get_by_text("Reporter Business")).to_be_visible()
#         expect(self.page.get_by_text("DBT")).not_to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#
# class TestCheckYourAnswersPersonOrBusinessYouAreReporting(conftest.PlaywrightTestBase):
#     """
#     Tests for check your answers page, specific to the person or business you're reporting section
#     """
#
#     def test_can_change_uk_breacher_details(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Person or Business you're reporting").click()
#         self.page.get_by_text("Name", exact=True).click()
#         # Change name
#         self.page.get_by_role("link", name="Change person or business name").click()
#         expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
#         self.page.get_by_label("Name of business or person").fill("Breaching Company")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("Breaching Company")).to_be_visible()
#         # Change website (remove it)
#         expect(self.page.get_by_text("Website", exact=True)).to_have_count(1)
#         self.page.get_by_role("link", name="Change person or business website").click()
#         expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
#         self.page.get_by_label("Website address (optional)").fill("")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page.get_by_text("Website", exact=True)).to_have_count(0)
#         # Change address
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("Breach Lane, Breach Avenue, Breach Town, BB0 0BB, United Kingdom")).to_be_visible()
#         self.page.get_by_role("link", name="Change  person or business address").click()
#         self.page.get_by_label("Town or city").click()
#         self.page.get_by_label("Town or city").fill("Another Town")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page.get_by_text("Breach Lane, Breach Avenue, Another Town, BB0 0BB, United Kingdom")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_non_uk_breacher_details(self):
#         self.page = self.create_breach(breach_details_third_party)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Person or Business you're reporting").click()
#         self.page.get_by_text("Name", exact=True).click()
#         # Change name
#         expect(self.page.get_by_text("German Breacher")).to_be_visible()
#         self.page.get_by_role("link", name="Change person or business name").click()
#         expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
#         self.page.get_by_label("Name of business or person").fill("Breaching Company")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("Breaching Company")).to_be_visible()
#         # Change website (remove it)
#         expect(self.page.get_by_text("Website", exact=True)).to_have_count(1)
#         self.page.get_by_role("link", name="Change person or business website").click()
#         expect(self.page).to_have_url(re.compile(r".*/business_or_person_details/.*"))
#         self.page.get_by_label("Website address (optional)").fill("")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page.get_by_text("Website", exact=True)).to_have_count(0)
#         # Change address
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("Germany Lane, Germany Avenue, Germany Town, Germany, Germany")).to_be_visible()
#
#         self.page.get_by_role("link", name="Change person or business address").click()
#         self.page.get_by_label("Address line 3 (optional)").click()
#         self.page.get_by_label("Address line 3 (optional)").fill("Another Line 3")
#         self.page.get_by_label("Country").select_option("VE")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page.get_by_text("Germany Lane, Germany Avenue, Germany Town, Venezuela, Venezuela")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_companies_house_details(self):
#         self.page = self.create_breach(breach_details_companies_house)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Person or business you're").click()
#         self.page.get_by_text("Registered company number", exact=True).click()
#         self.page.get_by_text("Name", exact=True).click()
#         self.page.get_by_text("12345678").click()
#         self.page.get_by_text("BOCIOC M LIMITED", exact=True).click()
#         self.page.get_by_text("52 Avocet Close, CV23 0WU", exact=True).click()
#         self.page.get_by_role("link", name="Change registered company").click()
#         expect(self.page).to_have_url(re.compile(r".*/do_you_know_the_registered_company_number/.*"))
#
#         self.page.get_by_label("Yes").check()
#         self.page.get_by_label("Registered company number").click()
#         self.page.get_by_label("Registered company number").fill("12349876")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/check_company_details/.*"))
#
#         self.page.get_by_text("Registered company number", exact=True).click()
#         self.page.get_by_text("12349876").click()
#         self.page.get_by_text("Registered company name").click()
#         self.page.get_by_text("BISSOT PROPERTY MANAGEMENT LTD").click()
#         self.page.get_by_text("Registered office address").click()
#         self.page.get_by_text("-22 Wenlock Road, N1 7GU").click()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("Registered company number", exact=True)).to_be_visible()
#         expect(self.page.get_by_text("12349876")).to_be_visible()
#         expect(self.page.get_by_text("12345678")).not_to_be_visible()
#         self.page.get_by_text("BISSOT PROPERTY MANAGEMENT LTD", exact=True).click()
#         self.page.get_by_text("20-22 Wenlock Road, N1 7GU", exact=True).click()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#
# class TestCheckYourAnswersOverviewOfTheBreach(conftest.PlaywrightTestBase):
#     """
#     Tests for check your answers page, specific to the overview of the breach section
#     """
#
#     def test_can_change_date_first_suspected_breach(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="Overview of the breach").click()
#         self.page.get_by_text("When did you first suspect").click()
#         expect(self.page.get_by_text("Exact date 03/05/2024")).to_be_visible()
#         self.page.get_by_role("link", name="Change when you first").click()
#         expect(self.page).to_have_url(re.compile(r".*/when_did_you_first_suspect/.*"))
#         self.page.get_by_role("heading", name="Date you first suspected the").click()
#         self.page.get_by_label("Day").fill("1")
#         self.page.get_by_label("Month").fill("1")
#         self.page.get_by_label("Year").fill("11")
#         self.page.get_by_label("Approximate date").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_text("When did you first suspect").click()
#         expect(self.page.get_by_text("Approximate date 01/01/2011")).to_be_visible()
#         expect(self.page.get_by_text("Exact date 03/05/2024")).not_to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_sanctions_regimes_breached(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_text("Sanctions regimes breached").click()
#         expect(self.page.get_by_text("The Oscars Fireplaces")).to_be_visible()
#         self.page.get_by_role("link", name="Change sanctions regime").click()
#         expect(self.page).to_have_url(re.compile(r".*/which_sanctions_regime/.*"))
#
#         self.page.get_by_label("The Oscars").uncheck()
#         self.page.get_by_label("Fireplaces").uncheck()
#         self.page.get_by_label("The Tonys").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         self.page.get_by_text("Sanctions regimes breached").click()
#         expect(self.page.get_by_text("The Oscars Fireplaces")).not_to_be_visible()
#         expect(self.page.get_by_text("The Tonys")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_what_were_the_goods(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_text("What were the goods or").click()
#         expect(self.page.get_by_text("Accountancy goods")).to_be_visible()
#         self.page.get_by_role("link", name="Change details of the goods").click()
#         expect(self.page).to_have_url(re.compile(r".*/what_were_the_goods/.*"))
#
#         self.page.get_by_label("What were the goods or").fill("Technology goods")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("Accountancy goods")).not_to_be_visible()
#         expect(self.page.get_by_text("Technology goods")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#
# class TestCheckYourAnswersTheSupplyChain(conftest.PlaywrightTestBase):
#     """
#     Tests for check your answers page, specific to the supply chain section
#     """
#
#     # todo - can change all options: breach location, uk location,
#      non-uk location, I do not know, they have not been supplied yet
#     def test_can_change_location_of_supplier(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="The supply chain", exact=True).click()
#         self.page.get_by_role("heading", name="Supplier").click()
#         self.page.get_by_text("Location of supplier", exact=True).click()
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         expect(self.page.get_by_text("Outside the UK")).to_have_count(2)
#         self.page.get_by_role("link", name="Change location of supplier").click()
#         expect(self.page).to_have_url(re.compile(r".*/where_were_the_goods_supplied_from/.*"))
#         self.page.get_by_label("Outside the UK").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/about_the_supplier/.*"))
#         self.page.get_by_label("Country").select_option("VE")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(1)
#         expect(self.page.get_by_text("Outside the UK")).to_have_count(3)
#         expect(self.page.get_by_text("Supply Street, Supply Lane, Supply Town, Venezuela")).to_be_visible()
#
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_to_unknown_location_of_supplier(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="The supply chain", exact=True).click()
#         self.page.get_by_role("heading", name="Supplier").click()
#         self.page.get_by_text("Location of supplier", exact=True).click()
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         self.page.get_by_role("link", name="Change location of supplier").click()
#         expect(self.page).to_have_url(re.compile(r".*/where_were_the_goods_supplied_from/.*"))
#         self.page.get_by_label("I do not know").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(1)
#         expect(self.page.get_by_text("I do not know")).to_be_visible()
#         expect(self.page.get_by_text("Supply Street, Supply Lane, Supply Town, United Kingdom")).not_to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_name_and_address_of_supplier_to_unknown(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="The supply chain", exact=True).click()
#         self.page.get_by_role("heading", name="Supplier").click()
#         self.page.get_by_text("Location of supplier", exact=True).click()
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         self.page.get_by_role("link", name="Change name and address of supplier").click()
#         expect(self.page).to_have_url(re.compile(r".*/where_were_the_goods_supplied_from/.*"))
#         self.page.get_by_label("I do not know").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(1)
#         expect(self.page.get_by_text("I do not know")).to_be_visible()
#         expect(self.page.get_by_text("Supply Street, Supply Lane, Supply Town, United Kingdom")).not_to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_location_of_end_user(self):
#         breach_details_owner["end_users"] = ["end_user1", "end_user2", "end_user3"]
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="The supply chain", exact=True).click()
#         self.page.get_by_role("heading", name="End-user 1").click()
#         self.page.get_by_role("heading", name="End-user 2").click()
#         self.page.get_by_role("heading", name="End-user 3").click()
#         expect(self.page.get_by_text("End User1 AL1, AL2, Town")).to_be_visible()
#
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         expect(self.page.get_by_text("Outside the UK", exact=True)).to_have_count(2)
#         self.page.get_by_role("link", name="Change location of end-user 1").click()
#         expect(self.page).to_have_url(re.compile(r".*/where_were_the_goods_supplied_to/.*"))
#         self.page.get_by_label("Outside the UK").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/about_the_end_user/*"))
#         self.page.get_by_label("Country").select_option("AS")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/end_user_added/*"))
#
#         self.page.get_by_label("No").check()
#         self.page.get_by_role("button", name="Continue").click()
#
#         expect(self.page).to_have_url(re.compile(r".*/summary/*"))
#
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(1)
#         expect(self.page.get_by_text("Outside the UK", exact=True)).to_have_count(3)
#         expect(self.page.get_by_text("End User1 AL1, AL2, Town", exact=True)).not_to_be_visible()
#         expect(self.page.get_by_text("End User1 AL1, AL2, Town, American Samoa")).to_be_visible()
#
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_change_name_and_address_of_end_user(self):
#         breach_details_owner["end_users"] = ["end_user1", "end_user2", "end_user3"]
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="The supply chain", exact=True).click()
#         self.page.get_by_role("heading", name="End-user 1").click()
#         self.page.get_by_role("heading", name="End-user 2").click()
#         self.page.get_by_role("heading", name="End-user 3").click()
#         expect(self.page.get_by_text("End User2")).to_be_visible()
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         expect(self.page.get_by_text("Outside the UK", exact=True)).to_have_count(2)
#         self.page.get_by_role("link", name="Change name and address of end-user 2").click()
#         expect(self.page).to_have_url(re.compile(r".*/about_the_end_user/.*"))
#         self.page.get_by_label("Name of person (optional)").fill("Alex Good")
#         self.page.get_by_label("Country").select_option("AS")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/end_user_added/*"))
#         self.page.get_by_label("No").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary/*"))
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         expect(self.page.get_by_text("Outside the UK", exact=True)).to_have_count(2)
#         expect(self.page.get_by_text("End User2")).not_to_be_visible()
#         expect(self.page.get_by_text("Alex Good")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#     def test_can_add_another_end_user(self):
#         breach_details_owner["end_users"] = ["end_user1", "end_user2", "end_user3"]
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_role("heading", name="Check your answers").click()
#         self.page.get_by_role("heading", name="The supply chain", exact=True).click()
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         expect(self.page.get_by_text("Outside the UK", exact=True)).to_have_count(2)
#         self.page.get_by_role("link", name="Add another end-user end-user").click()
#         expect(self.page).to_have_url(re.compile(r".*/where_were_the_goods_supplied_to/.*"))
#         self.page = self.create_end_user(self.page, data.END_USERS["end_user4"])
#         expect(self.page).to_have_url(re.compile(r".*/end_user_added/*"))
#         self.page.get_by_label("No").check()
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary/*"))
#         expect(self.page.get_by_text("The UK", exact=True)).to_have_count(2)
#         expect(self.page.get_by_text("Outside the UK", exact=True)).to_have_count(3)
#         expect(self.page.get_by_text("End User4")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
#
#
# class TestCheckYourAnswersSanctionsBreachDetails(conftest.PlaywrightTestBase):
#     """
#     Tests for check your answers page, specific to the sanctions breach details section
#     """
#
#     # todo - change uploaded documents
#
#     def test_can_change_summary_of_the_breach(self):
#         self.page = self.create_breach(breach_details_owner)
#         self.page.get_by_text("Summary of the breach", exact=True).click()
#         expect(self.page.get_by_text("Happened a month ago")).to_be_visible()
#         self.page.get_by_role("link", name="Change summary of the breach").click()
#         expect(self.page).to_have_url(re.compile(r".*/tell_us_about_the_suspected_breach/.*"))
#         self.page.get_by_label("Give a summary of the breach").fill("Occured last year")
#         self.page.get_by_role("button", name="Continue").click()
#         expect(self.page).to_have_url(re.compile(r".*/summary"))
#         expect(self.page.get_by_text("Happened a month ago")).not_to_be_visible()
#         expect(self.page.get_by_text("Occured last year")).to_be_visible()
#         self.page.get_by_role("button", name="Continue").click()
#         self.declaration_and_complete_page(self.page)
