import os
import re

import pytest
from django.conf import settings
from django.test.testcases import TransactionTestCase
from playwright.sync_api import expect, sync_playwright

from . import data


class PlaywrightTestBase(TransactionTestCase):
    create_new_test_breach = True
    base_url = settings.BASE_FRONTEND_TESTING_URL

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=settings.HEADLESS)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

        super().tearDownClass()

    def setUp(self) -> None:
        """Create a new page for each test"""
        self.page = self.browser.new_page()

    def tearDown(self) -> None:
        """Close the page after each test"""
        self.page.close()

    @classmethod
    def get_form_step_page(cls, form_step):
        print(f"{cls.base_url}/{form_step}/")
        return f"{cls.base_url}/report_a_suspected_breach/{form_step}/"

    @classmethod
    def email_details(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_label("What is your email address?").click()
        page.get_by_label("What is your email address?").fill(details["email"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def verify_email(cls, page, details=data.EMAIL_DETAILS):
        page.get_by_role("heading", name="We've sent you an email").click()
        page.get_by_label("Enter the 6 digit security").fill(details["verify_code"])
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def verify_email_details(cls, page, details=data.EMAIL_DETAILS):
        #
        # Email page
        #
        page = cls.email_details(page, details)
        #
        # Verify page
        #
        page = cls.verify_email(page, details)

        return page

    @classmethod
    def fill_uk_address_details(cls, page, details=data.UK_ADDRESS_DETAILS):
        # UK Address Details Page
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill(details["name"])
        page.get_by_label("Name of business or person").press("Tab")
        page.get_by_label("Website address").fill(details["website"])
        page.get_by_label("Website address").press("Tab")
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Address line 1").press("Tab")
        page.get_by_label("Address line 2").fill(details["address_line_2"])
        page.get_by_label("Address line 2").press("Tab")
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("Town or city").press("Tab")
        page.get_by_label("County").fill(details["county"])
        page.get_by_label("County").press("Tab")
        page.get_by_label("Postcode").fill(details["postcode"])
        page.get_by_role("button", name="Continue").click()

        return page

    @classmethod
    def fill_non_uk_address_details(cls, page, details=data.NON_UK_ADDRESS_DETAILS):
        # NON UK Address Details Page
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill(details["name"])
        page.get_by_label("Name of business or person").press("Tab")
        page.get_by_label("Website address").fill(details["website"])
        page.get_by_label("Website address").press("Tab")
        page.get_by_label("Country").select_option(details["country"])
        page.get_by_label("Country").press("Tab")
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Address line 1").press("Tab")
        page.get_by_label("Address line 2").fill(details["address_line_2"])
        page.get_by_label("Address line 2").press("Tab")
        page.get_by_label("Address line 3").fill(details["address_line_3"])
        page.get_by_label("Address line 3").press("Tab")
        page.get_by_label("Address line 4").fill(details["address_line_4"])
        page.get_by_label("Address line 4").press("Tab")
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("Town or city").press("Tab")
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def summary_and_declaration_page(cls, page):
        #
        # Declaration Page
        #
        page.get_by_role("heading", name="Declaration").click()
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Continue").click()
        #
        # Complete Page
        #
        page.get_by_role("heading", name="Submission complete").click()
        page.get_by_text("Your reference number").click()
        page.get_by_role("heading", name="What happens next").click()
        page.get_by_text("We have sent you a").click()
        page.get_by_role("link", name="View and print your report").click()
        page.get_by_text("What did you think of this service? (takes 30 seconds)").click()
        page.get_by_role("link", name="What did you think of this").click()
        return page

    @classmethod
    def upload_documents_page(cls, page, files=data.FILES):
        #
        # Upload Documents Page
        #
        page.get_by_role("heading", name="Upload documents (optional)").click()
        page.get_by_text("You can upload items such as").click()
        page.get_by_text("Drag and drop files here or").click()
        page.get_by_text("Choose files").click()
        page.get_by_label("Upload a file").set_input_files(files)
        return page

    @classmethod
    def reporter_professional_relationship(cls, page, reporter_professional_relationship):
        #
        # Start page
        #
        page.get_by_role("heading", name="What is your professional").click()
        page.get_by_label(reporter_professional_relationship).check()
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_third_party_details(cls, page):
        # Start page
        page = cls.reporter_professional_relationship(page, "I work for a third party")

        # Email Verify
        page = cls.verify_email_details(page)

        # Name and business you work for
        page.get_by_role("heading", name="Your details").click()
        page.get_by_label("Full name").click()
        page.get_by_label("Full name").fill("John Smith")
        page.get_by_label("Business you work for").click()
        page.get_by_label("Business you work for").fill("DBT")
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_owner_details(cls, page):
        # Start page
        page = cls.reporter_professional_relationship(page, "I'm an owner, officer or")

        # Email Verify
        page = cls.verify_email_details(page)

        # Name
        page.get_by_label("What is your full name?").click()
        page.get_by_label("What is your full name?").fill("John Smith")
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_companies_house_details(cls, page):
        page.get_by_role("heading", name="Are you reporting a business").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Do you know the registered").click()
        page.get_by_label("Yes").check()
        page.get_by_label("Registered company number").click()
        page.get_by_label("Registered company number").fill("12345678")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Check company details").click()
        page.get_by_text("Registered company number", exact=True).click()
        page.get_by_text("12345678").click()
        page.get_by_text("Registered company name").click()
        page.get_by_text("BOCIOC M LIMITED").click()
        page.get_by_text("Registered office address").click()
        page.get_by_text("Avocet Close, CV23 0WU").click()
        page.locator("dd").filter(has_text="Changeregistered company").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Task list").click()
        return page

    @classmethod
    def create_uk_breacher(cls, page):
        page.get_by_role("heading", name="Are you reporting a business").click()
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Where is the address of the").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Business or person details").click()
        page = cls.fill_uk_address_details(page, details=data.UK_BREACHER_ADDRESS_DETAILS)
        return page

    @classmethod
    def create_non_uk_breacher(cls, page):
        page.get_by_role("heading", name="Are you reporting a business").click()
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Where is the address of the").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Business or person details").click()
        page = cls.fill_non_uk_address_details(page, details=data.NON_UK_BREACHER_ADDRESS_DETAILS)
        return page

    @classmethod
    def create_suspected_data(cls, page, exact):
        page.get_by_role("heading", name="Date you first suspected the").click()
        page.get_by_role("heading", name="Enter the exact date or an").click()
        page.get_by_label("Day").click()
        page.get_by_label("Day").fill("03")
        page.get_by_label("Month").click()
        page.get_by_label("Month").fill("05")
        page.get_by_label("Year").click()
        page.get_by_label("Year").fill("2024")
        page.get_by_role("heading", name="Is the date you entered exact").click()
        if exact:
            page.get_by_text("Exact date", exact=True).click()
        else:
            page.get_by_text("Approximate date", exact=True).click()
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_sanctions(cls, page, sanctions):
        page.get_by_role("heading", name="Which sanctions regimes do").click()
        page.get_by_text("Select all that apply").click()
        for sanction in sanctions:
            page.get_by_label(sanction).check()
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def overview_of_breach(cls, page, exact=True, sanctions=data.SANCTIONS):
        page = cls.create_suspected_data(page, exact)
        page = cls.create_sanctions(page, sanctions)
        page.get_by_label("What were the goods or").click()
        page.get_by_label("What were the goods or").fill("Accountancy goods")
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_uk_supplier(cls, page, details=data.UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        page = cls.fill_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_non_uk_supplier(cls, page, details=data.NON_UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("Outside the UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        page = cls.fill_non_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_breacher_as_supplier(cls, page, breacher_address):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label(breacher_address).check()
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_unknown_supplier(cls, page):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("I do not know", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_uk_made_available_supplier(cls, page, details=data.UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Made Available From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("They have not been supplied").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        page = cls.fill_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_non_uk_made_available_supplier(cls, page, details=data.NON_UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Made Available From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("They have not been supplied").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        page = cls.fill_non_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def no_end_users(cls, page):
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_text("This is the address of the").click()
        page.get_by_label("I do not know", exact=True).check()
        page.get_by_role("button", name="Continue").click()

    @classmethod
    def create_end_user(cls, page, end_user_details):
        # Where were the goods supplied to (end user page)
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_text("This is the address of the").click()
        page.get_by_label(end_user_details["location"], exact=True).check()
        page.get_by_role("button", name="Continue").click()

        # About the End User
        page.get_by_role("heading", name="About the end-user").click()
        page.get_by_role("heading", name="Name and digital contact").click()
        page.get_by_label("Name of person (optional)").fill(end_user_details["name"])
        page.get_by_label("Name of business (optional)").fill(end_user_details["business"])
        page.get_by_label("Email address (optional)").fill(end_user_details["email"])
        page.get_by_label("Website address (optional)").fill(end_user_details["website"])
        page.get_by_label("Address line 1 (optional)").fill(end_user_details["address_line_1"])
        page.get_by_label("Address line 2 (optional)").fill(end_user_details["address_line_2"])
        if end_user_details["location"] == "The UK":
            page.get_by_label("County (optional)").fill(end_user_details["county"])
            page.get_by_label("Postcode (optional)").fill(end_user_details["postcode"])
        else:
            page.get_by_label("Country").select_option(end_user_details["country"])
            page.get_by_label("Address line 1 (optional)").fill(end_user_details["address_line_3"])
            page.get_by_label("Address line 2 (optional)").fill(end_user_details["address_line_4"])
        page.get_by_label("Town or city (optional)").fill(end_user_details["town_or_city"])
        page.get_by_label("Additional contact details (").fill(end_user_details["additional_contact_details"])
        page.get_by_role("button", name="Continue").click()

        return page

    @classmethod
    def create_reporter_details(cls, page, relationship):
        # Start page
        page = cls.reporter_professional_relationship(page, relationship)
        # Email Verify
        page = cls.verify_email_details(page)
        # Name
        if relationship in ["I'm an owner", "I'm acting"]:
            page.get_by_label("What is your full name?").click()
            page.get_by_label("What is your full name?").fill("John Smith")
            page.get_by_role("button", name="Continue").click()
        elif relationship in ["I work for a third party", "No professional relationship"]:
            page.get_by_role("heading", name="Your details").click()
            page.get_by_label("Full name").click()
            page.get_by_label("Full name").fill("John Smith")
            page.get_by_label("Business you work for").click()
            page.get_by_label("Business you work for").fill("DBT")
            page.get_by_role("button", name="Continue").click()
        return page

    @classmethod
    def create_breach(cls, breach_details):
        new_browser = cls.playwright.chromium.launch(headless=True)
        context = new_browser.new_context()
        page = context.new_page()
        page.goto(cls.base_url)
        page.get_by_role("link", name="Reset session").click()

        # Tasklist
        page.get_by_role("heading", name="Task list").click()
        page.get_by_role("link", name="Your details").click()

        # 1. Your Details
        page = cls.create_reporter_details(page, breach_details["reporter_relationship"])

        # Tasklist
        page.get_by_role("heading", name="Task list").click()
        page.get_by_role("link", name="2. About the person or").click()

        # 2. About the person or business you're reporting

        if breach_details["breacher_location"] == "uk":
            page = cls.create_uk_breacher(page)
        elif breach_details["breacher_location"] == "non_uk":
            page = cls.create_non_uk_breacher(page)
        elif breach_details["breacher_location"] == "companies_house":
            page = cls.create_companies_house_details(page)
        # Tasklist
        page.get_by_role("heading", name="Task list").click()
        page.get_by_role("link", name="Overview of the suspected breach").click()

        # 3. Overview of the suspected breach
        page = cls.overview_of_breach(page, breach_details["exact_date"], breach_details["sanctions"])

        # Tasklist
        page.get_by_role("heading", name="Task list").click()
        page.get_by_role("link", name="The supply chain").click()

        if breach_details["supplier_location"] == "uk":
            page = cls.create_uk_supplier(page)
        elif breach_details["supplier_location"] == "non_uk":
            page = cls.create_non_uk_supplier(page)

        expect(page).to_have_url(re.compile(r".*/where_were_the_goods_supplied_to/.*"))
        if breach_details.get("end_users", False):
            for end_user in breach_details["end_users"][:-1]:
                page = cls.create_end_user(page, end_user_details=data.END_USERS[end_user])
                # Add more End User
                page.get_by_label("Yes").check()
                page.get_by_role("button", name="Continue").click()
            page = cls.create_end_user(page, end_user_details=data.END_USERS[breach_details["end_users"][-1]])

        # Do not add another End User
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()

        # Were There Other Addresses in the Supply Chain Page
        page.get_by_role("heading", name="Were there any other").click()
        page.get_by_label("Yes").check()
        page.get_by_text("Give all addresses").click()
        page.get_by_label("Give all addresses").fill("Addr supply chain")
        page.get_by_role("button", name="Continue").click()

        #
        # Upload Documents Page
        #
        page = cls.upload_documents_page(page)
        page.get_by_role("button", name="Continue").click()

        #
        # Give a Summary of the Suspected Breach Page
        #
        page.get_by_text("Give a summary of the breach", exact=True).click()
        page.get_by_text("You can also include anything").click()
        page.get_by_label("Give a summary of the breach").click()
        page.get_by_label("Give a summary of the breach").fill("Happened a month ago")
        page.get_by_role("button", name="Continue").click()

        #
        # Tasklist
        #
        page.get_by_role("heading", name="Task list").click()
        page.get_by_role("link", name="Continue").click()

        return page


@pytest.fixture()
def sample_upload_file():
    return [{"name": "test.txt", "mimeType": "text/plain", "buffer": b"test"}]
