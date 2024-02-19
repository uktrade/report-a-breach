from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django_countries.fields import CountryField

from report_a_breach.base_classes.models import BaseModel
from report_a_breach.question_content import (
    ADDITIONAL_INFORMATION,
    EMAIL,
    FULL_NAME,
    RELATIONSHIP,
    WHAT_WERE_THE_GOODS,
)


class Breach(BaseModel):
    PERSON_OR_COMPANY_CHOICES = (
        ("person", "Person"),
        ("company", "Company"),
    )

    reporter_professional_relationship = models.TextField(
        null=False,
        choices=RELATIONSHIP["choices"],
        verbose_name=RELATIONSHIP["text"],
    )
    reporter_email_address = models.EmailField(verbose_name=EMAIL["text"])
    reporter_full_name = models.CharField(verbose_name=FULL_NAME["text"], max_length=255)
    sanctions_regimes = models.ManyToManyField(
        "SanctionsRegime", through="SanctionsRegimeBreachThrough"
    )
    additional_information = models.TextField(verbose_name=ADDITIONAL_INFORMATION["text"])
    what_were_the_goods = models.TextField(verbose_name=WHAT_WERE_THE_GOODS["text"])


class PersonOrCompany(BaseModel):
    PERSON_OR_COMPANY_CHOICES = (
        ("person", "Person"),
        ("company", "Company"),
    )
    TYPE_OF_RELATIONSHIP_CHOICES = (
        ("breacher", "Breacher"),
        ("supplier", "Supplier"),
        ("recipient", "Recipient"),
    )
    person_or_company = models.CharField(
        null=False,
        choices=PERSON_OR_COMPANY_CHOICES,
        max_length=7,
    )
    name = models.TextField()
    website = models.URLField(null=True)
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(null=True)
    address_line_3 = models.TextField(null=True)
    address_line_4 = models.TextField(null=True)
    town_or_city = models.TextField()
    county = CountryField()
    postcode = models.TextField()
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
    type_of_relationship = models.CharField(choices=TYPE_OF_RELATIONSHIP_CHOICES, max_length=9)


class SanctionsRegimeBreachThrough(BaseModel):
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
    sanctions_regime = models.ForeignKey("SanctionsRegime", on_delete=models.CASCADE)


class SanctionsRegime(BaseModel):
    short_name = models.TextField()
    full_name = models.TextField()
    date_range = DateRangeField


class UploadedDocument(BaseModel):
    file = models.FileField()
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
