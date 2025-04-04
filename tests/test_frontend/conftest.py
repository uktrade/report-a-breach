import os
import re
import uuid
from datetime import timedelta
from unittest import mock
from unittest.mock import MagicMock

import notifications_python_client
import pytest
from core.sites import SiteName
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.sites.models import Site
from django.test import override_settings
from django.test.testcases import LiveServerTestCase
from django.utils import timezone
from django_chunk_upload_handlers.clam_av import VirusFoundInFileException
from playwright.sync_api import expect, sync_playwright
from report_a_suspected_breach.forms.forms_documents_and_details import (
    UploadDocumentsForm,
)
from report_a_suspected_breach.models import ReporterEmailVerification
from utils import notifier

from django_app.report_a_suspected_breach.exceptions import CompaniesHouseException

from . import data


@override_settings(DEBUG=True)
class PlaywrightTestBase(LiveServerTestCase):
    """Base class for Playwright tests. Sets up the Playwright browser, page per test, and deals with the Site objects."""

    @classmethod
    def setUpClass(cls) -> None:
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()

        # starting playwright stuff
        cls.playwright = sync_playwright().start()

        # playwright on CirlceCI exhibits some tricky behaviour whereby the HEADLESS argument is passed as a string
        # instead of a bool. CircleCI should always be headless anyway
        if "CIRCLECI" in os.environ:
            cls.browser = cls.playwright.firefox.launch(headless=True)
        else:
            cls.browser = cls.playwright.firefox.launch(headless=settings.HEADLESS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

        super().tearDownClass()

    def setUp(self) -> None:
        #  Create a new page for each test
        if settings.SAVE_VIDEOS:
            self.page = self.browser.new_page(record_video_dir="video-test-results/")
        else:
            self.page = self.browser.new_page()

        # need to re-create the Site objects to match the new port of the live server,
        # first we just need to get the original port
        first_site = Site.objects.first()
        self.original_port = first_site.domain.split(":")[-1]

        # deleting
        Site.objects.all().delete()

        # recreating with the new port
        Site.objects.create(
            name=SiteName.report_a_suspected_breach,
            domain=f"{SiteName.report_a_suspected_breach}:{self.server_thread.port}",
        )
        Site.objects.create(
            name=SiteName.view_a_suspected_breach,
            domain=f"{SiteName.view_a_suspected_breach}:{self.server_thread.port}",
        )

        # navigate to the base url and reset the session
        self.page.goto(self.base_url)
        self.page.get_by_role("link", name="Reset session").click()

    def tearDown(self) -> None:
        if settings.SAVE_VIDEOS:
            # Rename the video in the test results directory, so it's readable
            # 1231239190wei9cwice023r239230.webm -> video-test-results/ClassName-test_method.webm
            old_name = self.page.video.path()
            output_directory = settings.ROOT_DIR / "video-test-results"
            if not output_directory.is_dir():
                output_directory.mkdir()
            os.replace(old_name, settings.ROOT_DIR / f"video-test-results/{type(self).__name__}-{self._testMethodName}.webm")

        # resetting the Site objects to their original state
        Site.objects.all().delete()
        Site.objects.create(
            name=SiteName.report_a_suspected_breach,
            domain=f"{SiteName.report_a_suspected_breach}:{self.original_port}",
        )
        Site.objects.create(
            name=SiteName.view_a_suspected_breach,
            domain=f"{SiteName.view_a_suspected_breach}:{self.original_port}",
        )

        # close the page
        self.page.close()

    @property
    def base_host(self) -> str:
        return settings.REPORT_A_SUSPECTED_BREACH_DOMAIN.split(":")[0]

    @property
    def base_url(self) -> str:
        return f"http://{self.base_host}:{self.server_thread.port}"

    def get_form_step_page(self, form_step):
        return f"{self.base_url}/report/{form_step}"

    @staticmethod
    def email_details(page, details=data.EMAIL_DETAILS):
        page.get_by_label("What is your email address?").fill(details["email"])
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def verify_email(page, details=data.EMAIL_DETAILS):
        page.get_by_role("heading", name="We've sent you an email").click()
        page.get_by_label("Enter the 6 digit security").fill(details["verify_code"])
        page.get_by_role("button", name="Continue").click()

    def verify_email_details(self, page):
        self.email_details(page)
        self.verify_email(page)

    @staticmethod
    def fill_uk_address_details(page, details=data.UK_ADDRESS_DETAILS):
        # UK Address Details Page
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill(details["name"])
        page.get_by_label("Website address").fill(details["website"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Address line 2").fill(details["address_line_2"])
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_label("County").fill(details["county"])
        page.get_by_label("Postcode").fill(details["postcode"])
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def fill_non_uk_address_details(page, details=data.NON_UK_ADDRESS_DETAILS):
        # NON UK Address Details Page
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill(details["name"])
        page.get_by_label("Website address").fill(details["website"])
        page.get_by_label("Country").select_option(details["country"])
        page.get_by_label("Address line 1").fill(details["address_line_1"])
        page.get_by_label("Address line 2").fill(details["address_line_2"])
        page.get_by_label("Address line 3").fill(details["address_line_3"])
        page.get_by_label("Address line 4").fill(details["address_line_4"])
        page.get_by_label("Town or city").fill(details["town"])
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def declaration_and_complete_page(page):
        #
        # Declaration Page
        #
        page.get_by_role("heading", name="Declaration").click()
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Submit").click()
        #
        # Complete Page
        #
        page.get_by_role("heading", name="Submission complete").click()
        page.get_by_text("Your reference number").click()
        page.get_by_role("heading", name="What happens next").click()
        page.get_by_text("We've sent a confirmation").click()
        page.get_by_role("link", name="View and print your report")
        page.get_by_text("What did you think of this service? (takes 30 seconds)").click()
        page.get_by_role("link", name="What did you think of this").click()

    @staticmethod
    def upload_documents_page(page, files=data.FILES):
        #
        # Upload Documents Page
        #
        page.get_by_role("heading", name="Upload documents (optional)").click()
        page.get_by_text("You can upload items such as").click()
        page.get_by_text("Drag and drop files here or").click()
        page.get_by_label("Choose files").set_input_files(files)

    @staticmethod
    def reporter_professional_relationship(page, reporter_professional_relationship):
        #
        # Start page
        #
        page.get_by_role("heading", name="What is your professional").click()
        page.get_by_label(reporter_professional_relationship).check()
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def create_companies_house_details(page):
        page.get_by_role("heading", name="Are you reporting a business").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Do you know the registered").click()
        page.get_by_label("Yes").check()
        page.get_by_label("Registered company number").click()
        page.get_by_label("Registered company number").fill("00000001")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Check company details").click()
        page.get_by_text("Registered company number", exact=True).click()
        page.get_by_text("00000001").click()
        page.get_by_text("Registered company name").click()
        page.get_by_text("Test Company Name").click()
        page.get_by_text("Registered office address").click()
        page.get_by_text("52 Test St, Test City, CV12 3MD").click()
        page.get_by_role("button", name="Continue").click()

    def create_uk_breacher(self, page):
        page.get_by_role("heading", name="Are you reporting a business").click()
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Where is the address of the").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Business or person details").click()
        self.fill_uk_address_details(page, details=data.UK_BREACHER_ADDRESS_DETAILS)

    def create_non_uk_breacher(self, page):
        page.get_by_role("heading", name="Are you reporting a business").click()
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Where is the address of the").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="Business or person details").click()
        self.fill_non_uk_address_details(page, details=data.NON_UK_BREACHER_ADDRESS_DETAILS)

    @staticmethod
    def create_suspected_data(page, exact):
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

    @staticmethod
    def create_sanctions(page, sanctions):
        page.get_by_role("heading", name="Which sanctions regimes do").click()
        page.get_by_text("Select all that apply").click()
        for sanction in sanctions:
            page.get_by_label(sanction).check()
        page.get_by_role("button", name="Continue").click()
        return page

    def overview_of_breach(self, page, exact=True, sanctions=data.SANCTIONS):
        self.create_suspected_data(page, exact)
        self.create_sanctions(page, sanctions)
        page.get_by_label("What were the goods or").click()
        page.get_by_label("What were the goods or").fill("Accountancy goods")
        page.get_by_role("button", name="Continue").click()

    def create_uk_supplier(self, page, details=data.UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        self.fill_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()

    def create_non_uk_supplier(self, page, details=data.NON_UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("Outside the UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        self.fill_non_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def create_breacher_as_supplier(page, breacher_address):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label(breacher_address).check()
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def create_unknown_supplier(page):
        # Where Were the Goods Supplied From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("I do not know", exact=True).check()
        page.get_by_role("button", name="Continue").click()

    def create_uk_made_available_supplier(self, page, details=data.UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Made Available From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("They have not been supplied").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        self.fill_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()

    def create_non_uk_made_available_supplier(self, page, details=data.NON_UK_SUPPLIER_ADDRESS_DETAILS):
        # Where Were the Goods Made Available From Page
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_label("They have not been supplied").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("heading", name="About the supplier").click()
        self.fill_non_uk_address_details(page, details=details)
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def no_end_users(page):
        page.get_by_role("heading", name="Where were the goods").click()
        page.get_by_text("This is the address of the").click()
        page.get_by_label("I do not know", exact=True).check()
        page.get_by_role("button", name="Continue").click()

    @staticmethod
    def create_end_user(page, end_user_details):
        # Where were the goods supplied to (end user page)
        page.get_by_role("heading", name="Where were the goods,").click()
        page.get_by_text("This is the address of the").click()
        page.get_by_label(end_user_details["location"], exact=True).check()
        page.get_by_role("button", name="Continue").click()

        # About the End User
        page.get_by_role("heading", name="End-user").click()
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

    def create_reporter_details(self, page, relationship):
        # Start page
        self.reporter_professional_relationship(page, relationship)
        # Email Verify
        self.verify_email_details(page)
        # Name
        if relationship in ["I'm an owner", "I'm acting"]:
            page.get_by_label("What is your full name?").fill("John Smith")
            page.get_by_role("button", name="Continue").click()
        elif relationship in ["I work for a third party", "No professional relationship"]:
            page.get_by_role("heading", name="Your details").click()
            page.get_by_label("Full name").click()
            page.get_by_label("Full name").fill("John Smith")
            page.get_by_label("Business you work for").click()
            page.get_by_label("Business you work for").fill("DBT")
            page.get_by_role("button", name="Continue").click()

    def create_breach(self, page, breach_details):
        # Tasklist
        page.get_by_role("heading", name="Report a suspected breach of trade sanctions", exact=True).click()
        page.get_by_role("link", name="Your details").click()

        # 1. Your Details
        self.create_reporter_details(page, breach_details["reporter_relationship"])

        # Tasklist
        page.get_by_role("heading", name="Report a suspected breach of trade sanctions", exact=True).click()
        page.get_by_role("link", name="Name and address of the person or").click()

        # Name and address of the person or business you're reporting

        if breach_details["breacher_location"] == "uk":
            self.create_uk_breacher(page)
        elif breach_details["breacher_location"] == "non_uk":
            self.create_non_uk_breacher(page)
        elif breach_details["breacher_location"] == "companies_house":
            self.create_companies_house_details(page)
        # Tasklist
        page.get_by_role("heading", name="Report a suspected breach of trade sanctions", exact=True).click()
        page.get_by_role("link", name="Overview of the suspected breach").click()

        # 3. Overview of the suspected breach
        self.overview_of_breach(page, breach_details["exact_date"], breach_details["sanctions"])

        # Tasklist
        page.get_by_role("heading", name="Report a suspected breach of trade sanctions", exact=True).click()
        page.get_by_role("link", name="People and businesses involved").click()

        if breach_details["supplier_location"] == "uk":
            self.create_uk_supplier(page)
        elif breach_details["supplier_location"] == "non_uk":
            self.create_non_uk_supplier(page)

        expect(page).to_have_url(re.compile(r".*/location-of-end-user"))
        if breach_details.get("end_users", False):
            for end_user in breach_details["end_users"][:-1]:
                self.create_end_user(page, end_user_details=data.END_USERS[end_user])
                # Add more End User
                page.get_by_label("Yes").check()
                page.get_by_role("button", name="Continue").click()
            self.create_end_user(page, end_user_details=data.END_USERS[breach_details["end_users"][-1]])

        # Do not add another End User
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()

        # Were any other people or businesses involved in the trade page
        if breach_details.get("no_others_in_supply_chain", False):
            page.get_by_role("heading", name="Were any other people or businesses").click()
            page.get_by_label("No", exact=True).check()
            page.get_by_role("button", name="Continue").click()
        else:
            page.get_by_role("heading", name="Were any other people or businesses").click()
            page.get_by_label("Yes").check()
            page.get_by_text("Give all names and addresses").click()
            page.get_by_label("Give all names and addresses").fill("Addr supply chain")
            page.get_by_role("button", name="Continue").click()

        #
        # Upload Documents Page
        #
        self.page.get_by_role("link", name="Sanctions breach details").click()
        self.upload_documents_page(page)
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
        page.get_by_role("heading", name="Report a suspected breach of trade sanctions", exact=True).click()
        page.get_by_role("link", name="Review and submit").click()


@pytest.fixture(autouse=True, scope="function")
def bypass_login(monkeypatch, staff_user):
    """Overrides the get_user function to always return the staff user without authentication.

    Effectively bypasses the login process for all frontend tests.
    """

    def patched_get_user(request):
        return staff_user

    monkeypatch.setattr("django.contrib.auth.get_user", patched_get_user)

    yield


@pytest.fixture(autouse=True)
def patched_send_email(monkeypatch):
    """We don't want to send emails when running front-end tests"""
    mock_notifications_api_client = mock.create_autospec(notifications_python_client.notifications.NotificationsAPIClient)
    monkeypatch.setattr(notifier, "NotificationsAPIClient", mock_notifications_api_client)


@pytest.fixture(autouse=True)
def patched_verify_code(monkeypatch):
    """Ensure the verify code is always the same for front end tests"""
    verify_code = "012345"
    test_session_key = uuid.uuid4()
    expire_date = timezone.now() + timedelta(minutes=10)
    user_session = Session.objects.create(session_key=test_session_key, expire_date=expire_date)
    patched_email_verification_obj = ReporterEmailVerification.objects.create(
        reporter_session=user_session,
        email_verification_code=verify_code,
    )

    monkeypatch.setattr("utils.notifier.verify_email", patched_email_verification_obj)

    mock_objects = MagicMock()
    mock_objects.filter.return_value.latest.return_value = patched_email_verification_obj

    monkeypatch.setattr("report_a_suspected_breach.forms.forms_start.ReporterEmailVerification.objects", mock_objects)


@pytest.fixture(autouse=True)
def patched_get_details_from_companies_house(monkeypatch):
    def mock_get_details_from_companies_house(test_str):
        test_company_details = {
            "company_number": "00000001",
            "company_name": "Test Company Name",
            "registered_office_address": {
                "address_line_1": "52 Test St",
                "locality": "Test City",
                "postal_code": "CV12 3MD",
                "country": "England",
            },
        }

        other_company_details = {
            "company_number": "00000002",
            "company_name": "Other Company Name",
            "registered_office_address": {
                "address_line_1": "20-22 Test Road",
                "locality": "Test town",
                "postal_code": "EX11 2MD",
                "country": "England",
            },
        }

        if test_str == test_company_details["company_number"]:
            return test_company_details

        elif test_str == other_company_details["company_number"]:
            return other_company_details

        else:
            raise CompaniesHouseException("Companies House API request failed: 400")

    monkeypatch.setattr("utils.companies_house.get_details_from_companies_house", mock_get_details_from_companies_house)


@pytest.fixture
def patched_clean_document(monkeypatch):
    mock_document = MagicMock()
    mock_document.readline.side_effect = VirusFoundInFileException
    original_clean_document = UploadDocumentsForm.clean_document

    def mock_clean_document(self):
        self.cleaned_data["document"] = [mock_document]
        return original_clean_document(self)

    monkeypatch.setattr(UploadDocumentsForm, "clean_document", mock_clean_document)
