from report_a_suspected_breach.models import Breach

from tests.test_frontend.conftest import PlaywrightTestBase


class TestMadeAvailableToFromPath(PlaywrightTestBase):
    def test_made_available_to_from_path(self):
        Breach.objects.all().delete()
        assert Breach.objects.all().count() == 0

        page = self.page
        page.goto(self.base_url)
        page.get_by_role("link", name="Your details").click()
        page.get_by_label("I do not have a professional").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What is your email address?").click()
        page.get_by_label("What is your email address?").fill("test@example.com")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Enter the 6 digit security").click()
        page.get_by_label("Enter the 6 digit security").fill("012345")
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Full name").click()
        page.get_by_label("Full name").fill("Chris")
        page.get_by_label("Full name").press("Tab")
        page.get_by_label("Business you work for").fill("DBT")
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
        page.get_by_label("Year").fill("13")
        page.get_by_label("Exact date").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Other regime").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("What were the goods or").click()
        page.get_by_label("What were the goods or").fill("what were the goods")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="The supply chain").click()
        page.get_by_label("They have not been supplied").check()
        page.get_by_role("button", name="Continue").click()
        page.locator("[name='where_were_the_goods_made_available_from']").first.click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("The UK", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Name of person (optional)").click()
        page.get_by_label("Name of person (optional)").fill("end user 1 - made available too")
        page.get_by_label("Name of business (optional)").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("No", exact=True).check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Sanctions breach details").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Give a summary of the breach").click()
        page.get_by_label("Give a summary of the breach").fill("summary")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("link", name="Review and submit").click()
        page.get_by_role("link", name="Continue").click()
        page.get_by_label("I agree and accept").check()
        page.get_by_role("button", name="Submit").click()

        assert Breach.objects.all().count() == 1
        breach = Breach.objects.first()

        assert breach.reporter_professional_relationship == "no_professional_relationship"
        assert breach.reporter_email_address == "test@example.com"
        assert breach.reporter_full_name == "Chris"
        assert breach.reporter_name_of_business_you_work_for == "DBT"

        entities = breach.personorcompany_set.all()
        assert entities.count() == 2  # 1 end-user and 1 breacher/supplier
        assert entities.filter(type_of_relationship="recipient").count() == 1
        assert entities.filter(type_of_relationship="breacher").count() == 1

        breacher = entities.get(type_of_relationship="breacher")
        assert breacher.name == "Test Company Name"
        assert breacher.registered_company_number == "00000001"
        assert breacher.address_line_1 == "52 Test St"
        assert breacher.postal_code == "CV12 3MD"
        assert breacher.town_or_city == "Test City"

        end_user = entities.get(type_of_relationship="recipient")
        assert end_user.name == "end user 1 - made available too"
