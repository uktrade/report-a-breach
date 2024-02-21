from crispy_forms_gds.choices import Choice
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
    Choice
    YES_NO_DO_NOT_KNOW_CHOICES = (
        ("yes", "Yes"),
        ("no", "No"),
        ("do_not_know", "I do not know"),
    )
    YES_NO_CHOICES = (
        ("yes", "Yes"),
        ("no", "No"),
    )

    reporter_professional_relationship = models.TextField(
        null=False,
        blank=False,
        choices=RELATIONSHIP["choices"],
        verbose_name=RELATIONSHIP["text"],
    )
    reporter_email_address = models.EmailField(verbose_name=EMAIL["text"])
    reporter_full_name = models.TextField(verbose_name=FULL_NAME["text"])
    sanctions_regimes = models.ManyToManyField(
        "SanctionsRegime", through="SanctionsRegimeBreachThrough"
    )
    additional_information = models.TextField(verbose_name=ADDITIONAL_INFORMATION["text"])
    what_were_the_goods = models.TextField(verbose_name=WHAT_WERE_THE_GOODS["text"])
    business_registered_on_companies_house = models.CharField(
        choices=YES_NO_DO_NOT_KNOW_CHOICES,
        max_length=11,
        verbose_name="Are you reporting a business which is registered with Companies House?",
        blank=False,
    )
    do_you_know_the_registered_company_number = models.CharField(
        choices=YES_NO_CHOICES,
        max_length=3,
        verbose_name="Do you know the registered company number?",
        blank=False,
    )
    registered_company_number = models.CharField(max_length=20, null=True, blank=True)


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
