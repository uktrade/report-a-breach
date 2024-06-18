import uuid

from core.models import BaseModel
from django.contrib.postgres.fields import DateRangeField
from django.contrib.sessions.models import Session
from django.db import models
from django_chunk_upload_handlers.clam_av import validate_virus_check_result
from django_countries.fields import CountryField

from . import choices


class Breach(BaseModel):
    reporter_professional_relationship = models.TextField(
        null=False, blank=False, choices=choices.ReporterProfessionalRelationshipChoices.choices
    )
    reporter_email_address = models.EmailField()
    reporter_email_verification = models.ForeignKey("ReporterEmailVerification", on_delete=models.CASCADE, blank=True, null=True)
    reference = models.CharField(null=True, blank=True, max_length=6)
    reporter_full_name = models.CharField(max_length=255)
    reporter_name_of_business_you_work_for = models.CharField(max_length=300, verbose_name="Business you work for")
    when_did_you_first_suspect = models.DateField()
    is_the_date_accurate = models.CharField(choices=choices.IsTheDateAccurateChoices.choices, max_length=11)
    sanctions_regimes = models.ManyToManyField("SanctionsRegime", through="SanctionsRegimeBreachThrough", blank=True)
    unknown_sanctions_regime = models.BooleanField(blank=True, default=False)
    where_were_the_goods_supplied_from = models.TextField()
    other_sanctions_regime = models.BooleanField(blank=True, default=False)
    what_were_the_goods = models.TextField()
    business_registered_on_companies_house = models.CharField(
        choices=choices.YesNoDoNotKnowChoices.choices,
        max_length=11,
        blank=False,
    )
    were_there_other_addresses_in_the_supply_chain = models.CharField(
        choices=choices.YesNoDoNotKnowChoices.choices,
        max_length=11,
        blank=False,
    )
    other_addresses_in_the_supply_chain = models.TextField(null=True, blank=True)
    tell_us_about_the_suspected_breach = models.TextField(null=True, blank=False)

    def assign_reference(self) -> str:
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
    verified = models.BooleanField(default=False)


class PersonOrCompany(BaseModel):
    name = models.TextField()
    name_of_business = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
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
    additional_contact_details = models.TextField(null=True, blank=True)
    type_of_relationship = models.CharField(choices=choices.TypeOfRelationshipChoices.choices, max_length=9)
    do_you_know_the_registered_company_number = models.CharField(
        choices=choices.YesNoChoices.choices,
        max_length=3,
        blank=False,
    )
    registered_company_number = models.CharField(max_length=20, null=True, blank=True)
    registered_office_address = models.CharField(null=True, blank=True)
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE)


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
