import datetime

from report_a_suspected_breach.models import Breach

from tests.test_frontend.conftest import PlaywrightTestBase


class TestThirdPartyPath(PlaywrightTestBase):
    def test_third_party_path(self):
        Breach.objects.all().delete()
        assert Breach.objects.all().count() == 0

        page = self.page
        page.get_by_role("link", name="Your details").click()
        page.get_by_label("I work for a third party with").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What is your email address?").click()
        page.get_by_label("What is your email address?").fill("test@example.com")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Enter the 6 digit security").click()
        page.get_by_label("Enter the 6 digit security").fill("012345")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Full name").click()
        page.get_by_label("Full name").fill("Test User")
        page.get_by_label("Business you work for").click()
        page.get_by_label("Business you work for").fill("DBT")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="2. Name and address of the person or").click()
        page.get_by_label("I do not know").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Outside the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill("Outside the UK Breacher ")
        page.get_by_label("Website address (optional)").click()
        page.get_by_label("Website address (optional)").fill("www.outsidetheukbreacher.com")
        page.get_by_label("Country").select_option("BS")
        page.get_by_label("Address line 1 (optional)").click()
        page.get_by_label("Address line 1 (optional)").fill("12 address 1")
        page.get_by_label("Address line 2 (optional)").click()
        page.get_by_label("Address line 2 (optional)").fill("address 2")
        page.get_by_label("Address line 3 (optional)").click()
        page.get_by_label("Address line 3 (optional)").fill("address 3")
        page.get_by_label("Address line 4 (optional)").click()
        page.get_by_label("Address line 4 (optional)").fill("address 4")
        page.get_by_label("Town or city (optional)").click()
        page.get_by_label("Town or city (optional)").fill("township")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Overview of the suspected breach").click()
        page.get_by_label("Day").click()
        page.get_by_label("Day").fill("1")
        page.get_by_label("Month").click()
        page.get_by_label("Month").fill("1")
        page.get_by_label("Year").click()
        page.get_by_label("Year").fill("3")
        page.get_by_label("Exact date").check()
        page.get_by_label("Year").click(click_count=3)
        page.get_by_label("Year").fill("13")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Other regime").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What were the goods or").click()
        page.get_by_label("What were the goods or").fill("what were the goods")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="People and businesses involved").click()
        page.get_by_text("The UK", exact=True).click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of business or person").click()
        page.get_by_label("Name of business or person").fill("Supplier LTD")
        page.get_by_label("Website address (optional)").click()
        page.get_by_label("Website address (optional)").fill("www.supplier.com")
        page.get_by_label("Address line 1").click()
        page.get_by_label("Address line 1").fill("12 supplier road")
        page.get_by_label("Address line 2 (optional)").click()
        page.get_by_label("Address line 2 (optional)").fill("ddress 2")
        page.get_by_text("Town or city").click()
        page.get_by_label("Town or city").click()
        page.get_by_label("Town or city").fill("york")
        page.get_by_label("County (optional)").click()
        page.get_by_label("County (optional)").fill("yorkshire")
        page.get_by_label("Postcode").click()
        page.get_by_label("Postcode").fill("sw1a 1aa")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of person (optional)").click()
        page.get_by_label("Name of person (optional)").fill("End User 1")
        page.get_by_label("Name of business (optional)").click()
        page.get_by_label("Name of business (optional)").fill("End User Ltd")
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

        assert breach.reporter_professional_relationship == "third_party"
        assert breach.reporter_full_name == "Test User"
        assert breach.reporter_email_address == "test@example.com"
        assert breach.reporter_name_of_business_you_work_for == "DBT"

        assert breach.sanctions_regimes_breached == ["Other Regime"]

        assert breach.when_did_you_first_suspect == datetime.date(2013, 1, 1)
        assert breach.is_the_date_accurate == "exact"

        assert breach.what_were_the_goods == "what were the goods"
        assert breach.where_were_the_goods_supplied_from == "different_uk_address"
        assert breach.tell_us_about_the_suspected_breach == "summary of the breach"

        entities = breach.personorcompany_set.all()
        assert entities.count() == 3  # 1 end-user, 1 breacher, 1 supplier
        assert entities.filter(type_of_relationship="recipient").count() == 1
        assert entities.filter(type_of_relationship="breacher").count() == 1
        assert entities.filter(type_of_relationship="supplier").count() == 1

        breacher = entities.get(type_of_relationship="breacher")
        assert breacher.name == "Outside the UK Breacher"
        assert breacher.website == "http://www.outsidetheukbreacher.com"
        assert breacher.address_line_1 == "12 address 1"
        assert breacher.address_line_2 == "address 2"
        assert breacher.address_line_3 == "address 3"
        assert breacher.address_line_4 == "address 4"
        assert breacher.town_or_city == "township"
        assert breacher.country == "BS"

        supplier = entities.get(type_of_relationship="supplier")
        assert supplier.name == "Supplier LTD"
        assert supplier.website == "http://www.supplier.com"
        assert supplier.address_line_1 == "12 supplier road"
        assert supplier.address_line_2 == "ddress 2"
        assert supplier.town_or_city == "york"
        assert supplier.county == "yorkshire"
        assert supplier.postal_code == "sw1a 1aa"

        end_user = entities.get(type_of_relationship="recipient")
        assert end_user.name == "End User 1"
        assert end_user.name_of_business == "End User Ltd"
