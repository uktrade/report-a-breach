import string

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyText


class BreachFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.Breach"

    when_did_you_first_suspect = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    where_were_the_goods_supplied_from = factory.Faker(
        "random_element",
        elements=["same_address", "different_uk_address", "outside_the_uk", "they_have_not_been_supplied", "i_do_not_know"],
    )
    reference = FuzzyText(length=4, chars=string.ascii_uppercase + string.digits)


class BreacherandSupplierFactory(BreachFactory):
    class Meta:
        model = "report_a_suspected_breach.Breach"

    when_did_you_first_suspect = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    where_were_the_goods_supplied_from = "same_address"


class BreacherPersonOrCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.PersonOrCompany"

    name = factory.Faker("name")
    type_of_relationship = "breacher"


class BreacherCompaniesHouseCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.PersonOrCompany"

    registered_company_number = factory.Faker("random_int", min=11111111, max=99999999)
    name = factory.Faker("company")
    type_of_relationship = "breacher"


class SupplierPersonOrCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.PersonOrCompany"

    name = factory.Faker("name")
    type_of_relationship = "supplier"


class RecipientPersonOrCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.PersonOrCompany"

    name = factory.Faker("name")
    type_of_relationship = "recipient"


class BreachWith2SanctionsFactory(BreachFactory):
    breacher = factory.RelatedFactory(
        BreacherPersonOrCompanyFactory,
        factory_related_name="breach",
    )

    supplier = factory.RelatedFactory(SupplierPersonOrCompanyFactory, factory_related_name="breach")

    recipient1 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")

    recipient2 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")

    recipient3 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")


class BreachWithCompaniesHouseFactory(BreachFactory):
    breacher = factory.RelatedFactory(
        BreacherCompaniesHouseCompanyFactory,
        factory_related_name="breach",
    )
    recipient1 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")

    recipient2 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")


class BreachBreacherAndSupplierFactory(BreacherandSupplierFactory):
    breacher = factory.RelatedFactory(
        BreacherPersonOrCompanyFactory,
        factory_related_name="breach",
    )
    recipient1 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")

    recipient2 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")
