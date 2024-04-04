import uuid

from django.contrib.postgres.fields import DateRangeField
from django.contrib.sessions.models import Session
from django.contrib.sites.models import Site
from django.db import models
from django_chunk_upload_handlers.clam_av import validate_virus_check_result
from django_countries.fields import CountryField

from report_a_breach.base_classes.models import BaseModel


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
        choices=(
            ("owner", "I'm an owner, officer or employee of the business, or I am the person"),
            (
                "acting",
                "I do not work for the business or person, but I'm acting on their behalf to make a voluntary declaration",
            ),
            (
                "third_party",
                "I work for a third party with a legal responsibility to make a mandatory declaration",
            ),
            (
                "no_professional_relationship",
                "I do not have a professional relationship with the business or person, or I no longer have a professional "
                "relationship with them",
            ),
        ),
    )
    reporter_email_address = models.EmailField()
    reporter_email_verification = models.ForeignKey("ReporterEmailVerification", on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(null=True, blank=True, max_length=6)
    reporter_full_name = models.CharField(max_length=255)
    reporter_name_of_business_you_work_for = models.CharField(max_length=300, verbose_name="Business you work for")
    when_did_you_first_suspect = models.TextField()
    sanctions_regimes = models.ManyToManyField("SanctionsRegime", through="SanctionsRegimeBreachThrough", blank=True)
    unknown_sanctions_regime = models.BooleanField(blank=True, default=False)
    other_sanctions_regime = models.BooleanField(blank=True, default=False)
    additional_information = models.TextField()
    what_were_the_goods = models.TextField()
    business_registered_on_companies_house = models.CharField(
        choices=YES_NO_DO_NOT_KNOW_CHOICES,
        max_length=11,
        blank=False,
    )
    do_you_know_the_registered_company_number = models.CharField(
        choices=YES_NO_CHOICES,
        max_length=3,
        blank=False,
    )
    registered_company_number = models.CharField(max_length=20, null=True, blank=True)
    were_there_other_addresses_in_the_supply_chain = models.CharField(
        choices=YES_NO_DO_NOT_KNOW_CHOICES,
        max_length=11,
        blank=False,
    )
    other_addresses_in_the_supply_chain = models.TextField(null=True, blank=True)
    tell_us_about_the_suspected_breach = models.TextField(null=True, blank=True)

    sites = models.ManyToManyField(Site)

    def assign_reference(self):
        """Assigns a unique reference to this Breach object"""
        reference = uuid.uuid4().hex[:6].upper()
        if self.__class__.objects.filter(reference=reference).exists():
            return self.assign_reference()
        self.reference = reference
        self.save()
        return reference


class ReporterEmailVerification(BaseModel):
    reporter_session = models.ForeignKey(Session, on_delete=models.CASCADE)
    email_verification_code = models.CharField(max_length=6)
    date_created = models.DateTimeField(auto_now_add=True)


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
    website = models.URLField(null=True, blank=True)
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(null=True, blank=True)
    address_line_3 = models.TextField(null=True, blank=True)
    address_line_4 = models.TextField(null=True, blank=True)
    town_or_city = models.TextField()
    country = CountryField()
    county = models.TextField(null=True, blank=True)
    postal_code = models.TextField()
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
    type_of_relationship = models.CharField(choices=TYPE_OF_RELATIONSHIP_CHOICES, max_length=9)


class SanctionsRegimeBreachThrough(BaseModel):
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
    sanctions_regime = models.ForeignKey("SanctionsRegime", on_delete=models.CASCADE, blank=True, null=True)


class SanctionsRegime(BaseModel):
    short_name = models.TextField()
    full_name = models.TextField()
    date_range = DateRangeField(blank=True, null=True)


class UploadedDocument(BaseModel):
    file = models.FileField(
        validators=[
            validate_virus_check_result,
        ],
    )
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)
