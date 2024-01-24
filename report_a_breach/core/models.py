from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django_countries.fields import CountryField

from report_a_breach.base_classes.models import BaseModel


class Breach(BaseModel):
    REPORTER_PROFESSIONAL_RELATIONSHIP_CHOICES = (
        ("owner", "I'm an owner, officer or employee of the company, or I am the person"),
        (
            "acting",
            "I do not work for the company, but I'm acting on their behalf to make a voluntary declaration",
        ),
        (
            "third_party",
            "I work for a third party with a legal responsibility to make a mandatory declaration",
        ),
        (
            "no_professional_relationship",
            "I do not have a professional relationship with the company or person or I no longer have a professional relationship with them",
        ),
    )
    PERSON_OR_COMPANY_CHOICES = (
        ("person", "Person"),
        ("company", "Company"),
    )

    reporter_professional_relationship = models.TextField(
        null=False,
        choices=REPORTER_PROFESSIONAL_RELATIONSHIP_CHOICES,
        verbose_name="What is your professional relationship with the company or person suspected of breaching sanctions?",
    )
    reporter_email_address = models.EmailField(verbose_name="What is your email address?")
    reporter_full_name = models.TextField(verbose_name="What is your full name?")
    sanctions_regimes = models.ManyToManyField(
        "SanctionsRegime", through="SanctionsRegimeBreachThrough"
    )
    additional_information = models.TextField(verbose_name="Tell us about the suspected breach")


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
