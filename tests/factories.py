import random
import string

import factory
from django.utils import timezone
from factory.fuzzy import FuzzyText
from feedback.models import FeedbackItem


class ModelFieldLazyChoice(factory.LazyFunction):
    def __init__(self, model_class, field, *args, **kwargs):
        field = model_class._meta.get_field(field)
        choices = [choice[0] for choice in field.choices]
        super().__init__(function=lambda: random.choice(choices), *args, **kwargs)


class ArrayFieldLazyChoice(factory.LazyFunction):
    def __init__(self, model_class, field, *args, **kwargs):
        field = model_class._meta.get_field(field)

        choices = [choice[0] for choice in field.base_field.choices]
        super().__init__(function=lambda: random.choices(choices, k=random.randint(1, len(choices))), *args, **kwargs)


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
        factory_related_name="breach_report",
    )

    supplier = factory.RelatedFactory(SupplierPersonOrCompanyFactory, factory_related_name="breach_report")

    recipient1 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach_report")

    recipient2 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach_report")

    recipient3 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach_report")


class BreachWithCompaniesHouseFactory(BreachFactory):
    breacher = factory.RelatedFactory(
        BreacherCompaniesHouseCompanyFactory,
        factory_related_name="breach_report",
    )
    recipient1 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach_report")

    recipient2 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach_report")


class BreachBreacherAndSupplierFactory(BreacherandSupplierFactory):
    breacher = factory.RelatedFactory(
        BreacherPersonOrCompanyFactory,
        factory_related_name="breach_report",
    )
    recipient1 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach_report")

    recipient2 = factory.RelatedFactory(RecipientPersonOrCompanyFactory, factory_related_name="breach_report")


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeedbackItem

    rating = ModelFieldLazyChoice(FeedbackItem, "rating")
    did_you_experience_any_issues = ArrayFieldLazyChoice(FeedbackItem, "did_you_experience_any_issues")
    how_we_could_improve_the_service = factory.Faker("text")


class UploadedDocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "report_a_suspected_breach.UploadedDocument"

    breach = factory.SubFactory(BreachFactory)
    file = factory.django.FileField(filename="test.txt")
