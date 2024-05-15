import factory
from django.utils import timezone


class BreachFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.Breach"

    when_did_you_first_suspect = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())


class SanctionsRegimeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.SanctionsRegime"

    full_name = factory.Faker("name")


class SanctionsRegimeBreachThroughFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.SanctionsRegimeBreachThrough"

    breach = factory.SubFactory(BreachFactory)
    sanctions_regime = factory.SubFactory(SanctionsRegimeFactory)


class BreacherPersonOrCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.PersonOrCompany"

    name = factory.Faker("name")
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
    sanctions1 = factory.RelatedFactory(
        SanctionsRegimeBreachThroughFactory,
        factory_related_name="breach",
    )
    sanctions2 = factory.RelatedFactory(
        SanctionsRegimeBreachThroughFactory,
        factory_related_name="breach",
    )

    breacher = factory.RelatedFactory(
        BreacherPersonOrCompanyFactory,
        factory_related_name="breach",
    )

    supplier = factory.RelatedFactory(SupplierPersonOrCompanyFactory, factory_related_name="breach")

    recipient1 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")

    recipient2 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")

    recipient3 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach")


class CompaniesHouseCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.CompaniesHouseCompany"

    registered_company_number = factory.Faker("")
    breach = factory.SubFactory(BreachWith2SanctionsFactory)
