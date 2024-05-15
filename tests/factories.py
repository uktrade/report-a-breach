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


class BreachWith2SanctionsFactory(BreachFactory):
    membership1 = factory.RelatedFactory(
        SanctionsRegimeBreachThroughFactory,
        factory_related_name="breach",
    )
    membership2 = factory.RelatedFactory(
        SanctionsRegimeBreachThroughFactory,
        factory_related_name="breach",
    )
