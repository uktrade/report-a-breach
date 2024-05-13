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
