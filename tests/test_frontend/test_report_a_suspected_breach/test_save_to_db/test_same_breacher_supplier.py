import datetime

from report_a_suspected_breach.models import Breach

from tests.test_frontend.conftest import PlaywrightTestBase


class TestSameBreacherSupplierPath(PlaywrightTestBase):
    def test_same_supplier_breacher(self):
        Breach.objects.all().delete()
        assert Breach.objects.all().count() == 0

        page = self.page
        page.goto(self.base_url)
        page.get_by_role("link", name="Your details").click()
        page.get_by_label("I do not work for the").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What is your email address?").click()
        page.get_by_label("What is your email address?").fill("test@example.com")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Enter the 6 digit security").click()
        page.get_by_label("Enter the 6 digit security").fill("012345")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What is your full name?").click()
        page.get_by_label("What is your full name?").fill("Chris ")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="2. About the person or").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_label("Registered company number").click()
        page.get_by_label("Registered company number").fill("00000001")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Overview of the suspected breach").click()
        page.get_by_label("Day").click()
        page.get_by_label("Day").fill("1")
        page.get_by_label("Month").click()
        page.get_by_label("Month").fill("1")
        page.get_by_label("Year").click()
        page.get_by_label("Year").fill("14")
        page.get_by_label("Approximate date").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("The Afghanistan (Sanctions) (").check()
        page.get_by_label("I do not know").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What were the goods or").click()
        page.get_by_label("What were the goods or").fill("this isa. short description")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="The supply chain").click()
        page.locator("[name='where_were_the_goods_supplied_from']").first.click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of person (optional)").click()
        page.get_by_label("Name of person (optional)").fill("End User 1")
        page.get_by_label("Name of business (optional)").click()
        page.get_by_label("Name of business (optional)").fill("end user ltd")
        page.get_by_label("Email address (optional)").click()
        page.get_by_label("Email address (optional)").fill("enduser@example.com")
        page.get_by_label("Website address (optional)").click()
        page.get_by_label("Website address (optional)").fill("www.enduser1.com")
        page.get_by_label("Address line 1 (optional)").click()
        page.get_by_label("Address line 1 (optional)").fill("12 end user road")
        page.get_by_label("Address line 2 (optional)").click()
        page.get_by_label("Address line 2 (optional)").fill("end user flat")
        page.get_by_label("Town or city (optional)").click()
        page.get_by_label("Town or city (optional)").fill("london")
        page.get_by_label("County (optional)").click()
        page.get_by_label("County (optional)").fill("greater london")
        page.get_by_label("Postcode (optional)").click()
        page.get_by_label("Postcode (optional)").fill("sw1a 1aa")
        page.get_by_label("Additional contact details (").click()
        page.get_by_label("Additional contact details (").fill("fax machine: 12345")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Sanctions breach details").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Give a summary of the breach").click()
        page.get_by_label("Give a summary of the breach").fill("summary of the breach")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Review and submit").click()
        page.get_by_role("link", name="Continue").click()
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Submit").click()

        assert Breach.objects.all().count() == 1
        breach = Breach.objects.first()

        assert breach.reporter_professional_relationship == "acting"
        assert breach.reporter_email_address == "test@example.com"
        assert breach.reporter_full_name == "Chris"
        assert breach.reporter_name_of_business_you_work_for == "Test Company Name"
        assert len(breach.reference) == 6

        assert breach.sanctions_regimes_breached == ["Unknown Regime"]

        assert breach.when_did_you_first_suspect == datetime.date(2014, 1, 1)
        assert breach.is_the_date_accurate == "approximate"

        assert not breach.other_addresses_in_the_supply_chain
        assert breach.what_were_the_goods == "this isa. short description"

        # Check the entities
        entities = breach.personorcompany_set.all()
        assert entities.count() == 2  # 1 end-user and 1 breacher/supplier
        assert entities.filter(type_of_relationship="recipient").count() == 1
        assert entities.filter(type_of_relationship="breacher").count() == 1

        # Check the end-user
        end_user = entities.get(type_of_relationship="recipient")
        assert end_user.name == "End User 1"
        assert end_user.name_of_business == "end user ltd"
        assert end_user.email == "enduser@example.com"
        assert end_user.website == "http://www.enduser1.com"
        assert end_user.address_line_1 == "12 end user road"
        assert end_user.address_line_2 == "end user flat"
        assert end_user.town_or_city == "london"
        assert end_user.county == "greater london"
        assert end_user.postal_code == "sw1a 1aa"
        assert end_user.additional_contact_details == "fax machine: 12345"
        assert end_user.country == "GB"

        breacher = entities.get(type_of_relationship="breacher")
        assert breacher.name == "Test Company Name"
        assert breacher.registered_company_number == "00000001"
        assert breacher.country == "GB"
        assert breacher.address_line_1 == "52 Test St"
        assert breacher.town_or_city == "Test City"
        assert breacher.postal_code == "CV12 3MD"
