import uuid

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
    reference = models.CharField(null=True, blank=True, verbose_name="Reference", max_length=6)
    reporter_full_name = models.CharField(verbose_name=FULL_NAME["text"], max_length=255)
    reporter_name_of_business_you_work_for = models.CharField(max_length=300, verbose_name="Business you work for")
    sanctions_regimes = models.ManyToManyField("SanctionsRegime", through="SanctionsRegimeBreachThrough", blank=True)
    unknown_sanctions_regime = models.BooleanField(blank=True, default=False)
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
    were_there_other_addresses_in_the_supply_chain = models.CharField(
        choices=YES_NO_DO_NOT_KNOW_CHOICES,
        max_length=11,
        verbose_name="Were there any other addresses in the supply chain?",
        blank=False,
    )
    other_addresses_in_the_supply_chain = models.TextField(null=True, blank=True, verbose_name="Give all addresses")
    tell_us_about_the_suspected_breach = models.TextField(
        null=True, blank=True, verbose_name="Tell us about the suspected breach"
    )

    def assign_reference(self):
        """Assigns a unique reference to this Breach object"""
        reference = uuid.uuid4().hex[:6].upper()
        if self.__class__.objects.filter(reference=reference).exists():
            return self.assign_reference()
        self.reference = reference
        self.save()
        return reference


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
    name = models.TextField(verbose_name="Name of business or person")
    website = models.URLField(null=True, blank=True, verbose_name="Website address")
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(null=True, blank=True)
    address_line_3 = models.TextField(null=True, blank=True)
    address_line_4 = models.TextField(null=True, blank=True)
    town_or_city = models.TextField()
    country = CountryField()
    county = models.TextField(null=True)
    postal_code = models.TextField()
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
    type_of_relationship = models.CharField(choices=TYPE_OF_RELATIONSHIP_CHOICES, max_length=9)
    when_did_you_first_suspect = models.TextField(
        verbose_name="When did you first suspect the business or person had breached trade sanctions?"
    )


class SanctionsRegimeBreachThrough(BaseModel):
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
    sanctions_regime = models.ForeignKey("SanctionsRegime", on_delete=models.CASCADE, blank=True, null=True)


class SanctionsRegime(BaseModel):
    short_name = models.TextField()
    full_name = models.TextField()
    date_range = DateRangeField(blank=True, null=True)


class UploadedDocument(BaseModel):
    file = models.FileField()
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
