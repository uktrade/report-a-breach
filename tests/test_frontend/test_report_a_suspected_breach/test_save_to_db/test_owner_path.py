import datetime

from report_a_suspected_breach.models import Breach

from tests.test_frontend.conftest import PlaywrightTestBase


class TestOwnerPath(PlaywrightTestBase):
    def test_owner_path(self):
        Breach.objects.all().delete()
        assert Breach.objects.all().count() == 0

        page = self.page
        page.get_by_role("link", name="Your details").click()
        page.get_by_label("I'm an owner, officer or").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What is your email address?").click()
        page.get_by_label("What is your email address?").fill("test@example.com")
        page.get_by_label("What is your email address?").press("Enter")
        page.get_by_label("Enter the 6 digit security").fill("012345")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What is your full name?").click()
        page.get_by_label("What is your full name?").fill("Test User")
        page.get_by_label("What is your full name?").press("Enter")
        page.get_by_role("link", name="Name and address of the person or").click()
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("In the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill("Business Ltd")
        page.get_by_label("Name of business or person").press("Tab")
        page.get_by_label("Website address (optional)").fill("www.example.com")
        page.get_by_label("Website address (optional)").press("Tab")
        page.get_by_label("Address line 1").fill("12 business road")
        page.get_by_label("Address line 2 (optional)").click()
        page.get_by_label("Address line 2 (optional)").fill("address line 2")
        page.get_by_label("Town or city").click()
        page.get_by_label("Town or city").fill("london")
        page.get_by_label("County (optional)").click()
        page.get_by_label("County (optional)").fill("greater london")
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("SW1A 1AA")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Overview of the suspected breach").click()
        page.get_by_label("Day").click()
        page.get_by_label("Day").fill("1")
        page.get_by_label("Month").click()
        page.get_by_label("Month").fill("1")
        page.get_by_label("Year").click()
        page.get_by_label("Year").fill("14")
        page.get_by_label("Exact date").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("The Central African Republic").check()
        page.get_by_label("The Counter-Terrorism (").check()
        page.get_by_label("The Democratic People's").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What were the goods or").click()
        page.get_by_label("What were the goods or").fill("this is a short description, what were the goods")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="People and businesses involved").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill("Supplier Ltd")
        page.get_by_label("Name of business or person").press("Tab")
        page.get_by_label("Website address (optional)").fill("www.supplier.com")
        page.get_by_label("Website address (optional)").press("Tab")
        page.get_by_label("Address line 1").fill("12 supplier road")
        page.get_by_label("Address line 1").press("Tab")
        page.get_by_label("Town or city").click()
        page.get_by_label("Town or city").fill("manchester")
        page.get_by_label("Town or city").press("Tab")
        page.get_by_label("County (optional)").fill("greater manchester")
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("SW1W 9SP")
        page.get_by_role("button", name="Continue").click()
        page.get_by_text("The UK", exact=True).click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of person (optional)").click()
        page.get_by_label("Name of person (optional)").fill("End User 1")
        page.get_by_label("Email address (optional)").click()
        page.get_by_label("Email address (optional)").fill("enduser1@example.com")
        page.get_by_label("Email address (optional)").press("Tab")
        page.get_by_label("Website address (optional)").fill("www.enduser1.com")
        page.get_by_label("Website address (optional)").press("Tab")
        page.get_by_label("Address line 1 (optional)").fill("12 end user road")
        page.get_by_label("Address line 1 (optional)").press("Tab")
        page.get_by_label("Address line 2 (optional)").fill("end user 1")
        page.get_by_label("Town or city (optional)").click()
        page.get_by_label("Town or city (optional)").fill("york")
        page.get_by_label("Postcode (optional)").click()
        page.get_by_label("Postcode (optional)").fill("sw1w 0pp")
        page.get_by_label("Additional contact details (").click()
        page.get_by_label("Additional contact details (").fill("additonal contact details")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of person (optional)").click()
        page.get_by_label("Name of person (optional)").fill("End User 2")
        page.get_by_label("Email address (optional)").click()
        page.get_by_label("Email address (optional)").fill("enduser2@example.com")
        page.get_by_label("Website address (optional)").click()
        page.get_by_label("Website address (optional)").fill("www.enduser2.com")
        page.get_by_label("Country").select_option("AO")
        page.get_by_label("Address line 1 (optional)").click()
        page.get_by_label("Address line 1 (optional)").fill("12 end user 2 road")
        page.get_by_label("Address line 3 (optional)").click()
        page.get_by_label("Address line 3 (optional)").fill("address line 3")
        page.get_by_label("Address line 4 (optional)").click()
        page.get_by_label("Address line 4 (optional)").fill("address line 4")
        page.get_by_label("Town or city (optional)").click()
        page.get_by_label("Town or city (optional)").fill("angola city")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Yes").check()
        page.get_by_label("Give all names and addresses").click()
        page.get_by_label("Give all names and addresses").fill("other addresses")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Sanctions breach details").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Give a summary of the breach").click()
        page.get_by_label("Give a summary of the breach").fill("this is a summary of the breach")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Review and submit").click()
        page.get_by_role("link", name="Continue").click()
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Submit").click()

        assert Breach.objects.all().count() == 1
        breach = Breach.objects.first()

        # reporter details
        assert not breach.business_registered_on_companies_house
        assert breach.reporter_email_address == "test@example.com"
        assert breach.reporter_full_name == "Test User"
        assert breach.reporter_professional_relationship == "owner"

        # check the sanctions_regimes_breached details
        assert not breach.other_sanctions_regime
        assert not breach.unknown_sanctions_regime
        assert len(breach.sanctions_regimes_breached) == 3

        # other addresses
        assert breach.were_there_other_addresses_in_the_supply_chain == "yes"
        assert breach.other_addresses_in_the_supply_chain == "other addresses"

        assert breach.tell_us_about_the_suspected_breach == "this is a summary of the breach"
        assert breach.what_were_the_goods == "this is a short description, what were the goods"
        assert breach.where_were_the_goods_supplied_from == "different_uk_address"

        # date of breach
        assert breach.is_the_date_accurate == "exact"
        assert breach.when_did_you_first_suspect == datetime.date(2014, 1, 1)

        # people/businesses involved
        entities = breach.personorcompany_set.all()
        assert len(entities) == 4
        assert len(entities.filter(type_of_relationship="breacher")) == 1
        assert len(entities.filter(type_of_relationship="supplier")) == 1
        assert len(entities.filter(type_of_relationship="recipient")) == 2  # 2 end users

        # check the breacher details
        breacher = entities.get(type_of_relationship="breacher")
        assert breacher.address_line_1 == "12 business road"
        assert breacher.address_line_2 == "address line 2"
        assert breacher.name == "Business Ltd"
        assert breacher.postal_code == "SW1A 1AA"
        assert breacher.website == "http://www.example.com"
        assert breacher.town_or_city == "london"
        assert breacher.county == "greater london"
        assert breacher.country == "GB"

        supplier = entities.get(type_of_relationship="supplier")
        assert supplier.address_line_1 == "12 supplier road"
        assert supplier.name == "Supplier Ltd"
        assert supplier.postal_code == "SW1W 9SP"
        assert supplier.website == "http://www.supplier.com"
        assert supplier.town_or_city == "manchester"
        assert supplier.county == "greater manchester"
        assert supplier.country == "GB"

        # check the recipient details
        end_user_1 = entities.get(name="End User 1")
        assert end_user_1.address_line_1 == "12 end user road"
        assert end_user_1.address_line_2 == "end user 1"
        assert end_user_1.email == "enduser1@example.com"
        assert end_user_1.postal_code == "sw1w 0pp"
        assert end_user_1.town_or_city == "york"
        assert end_user_1.county == ""
        assert end_user_1.additional_contact_details == "additonal contact details"
        assert end_user_1.website == "http://www.enduser1.com"
        assert end_user_1.country == "GB"

        end_user_2 = entities.get(name="End User 2")
        assert end_user_2.address_line_1 == "12 end user 2 road"
        assert end_user_2.address_line_3 == "address line 3"
        assert end_user_2.address_line_4 == "address line 4"
        assert end_user_2.country == "AO"
        assert end_user_2.email == "enduser2@example.com"
        assert end_user_2.town_or_city == "angola city"
        assert end_user_2.website == "http://www.enduser2.com"
