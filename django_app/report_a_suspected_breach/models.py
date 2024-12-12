import uuid
from typing import TYPE_CHECKING

from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage
from core.models import BaseModel
from django.contrib.postgres.fields import ArrayField
from django.contrib.sessions.models import Session
from django.db import models, transaction
from django_chunk_upload_handlers.clam_av import validate_virus_check_result
from django_countries.fields import CountryField
from report_a_suspected_breach.form_step_conditions import (
    show_about_the_supplier_page,
    show_check_company_details_page_condition,
    show_name_and_business_you_work_for_page,
)
from utils.s3 import get_all_session_files, store_document_in_permanent_bucket

from .choices import TypeOfRelationshipChoices
from .exceptions import EmailNotVerifiedException
from .utils import get_all_cleaned_data

if TYPE_CHECKING:
    from django.http import HttpRequest

from . import choices


class Breach(BaseModel):
    reporter_professional_relationship = models.TextField(
        null=False, blank=False, choices=choices.ReporterProfessionalRelationshipChoices.choices
    )
    reporter_email_address = models.EmailField()
    reporter_email_verification = models.ForeignKey("ReporterEmailVerification", on_delete=models.SET_NULL, blank=True, null=True)
    reference = models.CharField(null=True, blank=True, max_length=6)
    reporter_full_name = models.CharField(max_length=255)
    reporter_name_of_business_you_work_for = models.CharField(max_length=300, verbose_name="Business you work for")
    when_did_you_first_suspect = models.DateField()
    is_the_date_accurate = models.CharField(choices=choices.IsTheDateAccurateChoices.choices, max_length=11)
    unknown_sanctions_regime = models.BooleanField(blank=True, default=False)
    where_were_the_goods_supplied_from = models.TextField()
    sanctions_regimes_breached = ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True, default=list)
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
    reporter_session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)

    def assign_reference(self) -> str:
        """Assigns a unique reference to this Breach object"""
        reference = uuid.uuid4().hex[:6].upper()
        if self.__class__.objects.filter(reference=reference).exists():
            return self.assign_reference()
        self.reference = reference
        self.save()
        return reference

    @classmethod
    def create_from_session(cls, request: "HttpRequest") -> "Breach":
        """Creates a Breach object from the data stored in current session"""
        cleaned_data = get_all_cleaned_data(request)
        if show_name_and_business_you_work_for_page(request):
            reporter_full_name = cleaned_data["name_and_business_you_work_for"]["reporter_full_name"]
            reporter_name_of_business_you_work_for = cleaned_data["name_and_business_you_work_for"][
                "reporter_name_of_business_you_work_for"
            ]
        else:
            reporter_full_name = cleaned_data["name"]["reporter_full_name"]
            if (
                cleaned_data.get("do_you_know_the_registered_company_number", {}).get(
                    "do_you_know_the_registered_company_number", ""
                )
                == "yes"
            ):
                reporter_name_of_business_you_work_for = cleaned_data["do_you_know_the_registered_company_number"][
                    "registered_company_name"
                ]
            else:
                reporter_name_of_business_you_work_for = cleaned_data["business_or_person_details"]["name"]

        # atomic transaction so that if any part of the process fails, the whole process is rolled back
        with transaction.atomic():
            reporter_email_verification = ReporterEmailVerification.objects.filter(
                reporter_session=request.session.session_key
            ).latest("date_created")

            if not reporter_email_verification.verified:
                # the user hasn't verified their email address, don't let them submit
                raise EmailNotVerifiedException()

            # Save Breach to Database
            new_breach = Breach.objects.create(
                reporter_professional_relationship=cleaned_data["start"]["reporter_professional_relationship"],
                reporter_email_address=cleaned_data["email"]["reporter_email_address"],
                reporter_email_verification=reporter_email_verification,
                reporter_full_name=reporter_full_name,
                reporter_name_of_business_you_work_for=reporter_name_of_business_you_work_for,
                when_did_you_first_suspect=cleaned_data["when_did_you_first_suspect"]["when_did_you_first_suspect"],
                is_the_date_accurate=cleaned_data["when_did_you_first_suspect"]["is_the_date_accurate"],
                what_were_the_goods=cleaned_data["what_were_the_goods"]["what_were_the_goods"],
                where_were_the_goods_supplied_from=cleaned_data["where_were_the_goods_supplied_from"][
                    "where_were_the_goods_supplied_from"
                ],
                were_there_other_addresses_in_the_supply_chain=cleaned_data["were_there_other_addresses_in_the_supply_chain"][
                    "were_there_other_addresses_in_the_supply_chain"
                ],
                other_addresses_in_the_supply_chain=cleaned_data["were_there_other_addresses_in_the_supply_chain"][
                    "other_addresses_in_the_supply_chain"
                ],
                tell_us_about_the_suspected_breach=cleaned_data["tell_us_about_the_suspected_breach"][
                    "tell_us_about_the_suspected_breach"
                ],
                reporter_session=request.session._get_session_from_db(),
            )

            if declared_sanctions := cleaned_data["which_sanctions_regime"]["which_sanctions_regime"]:
                new_breach.unknown_sanctions_regime = "Unknown Regime" in declared_sanctions
                new_breach.other_sanctions_regime = "Other Regime" in declared_sanctions

                new_breach.sanctions_regimes_breached = declared_sanctions

            # Save breacher details to database
            if show_check_company_details_page_condition(request):
                breacher_details = cleaned_data["do_you_know_the_registered_company_number"]
            else:
                breacher_details = cleaned_data["business_or_person_details"]

            PersonOrCompany.save_person_or_company(new_breach, breacher_details, TypeOfRelationshipChoices.breacher)

            # Save documents to permanent bucket and database
            UploadedDocument.save_documents(new_breach, request)
            # Save supplier details to database
            if show_about_the_supplier_page(request):
                supplier_details = cleaned_data["about_the_supplier"]
                PersonOrCompany.save_person_or_company(new_breach, supplier_details, TypeOfRelationshipChoices.supplier)

            # Save recipient(s) details to database
            if end_users := request.session.get("end_users", None):
                for end_user in end_users:
                    end_user_details = end_users[end_user]["cleaned_data"]
                    end_user_details["name"] = end_user_details.get("name_of_person", "")
                    PersonOrCompany.save_person_or_company(new_breach, end_user_details, TypeOfRelationshipChoices.recipient)

        new_breach.assign_reference()
        new_breach.save()
        return new_breach


class PersonOrCompany(BaseModel):
    @classmethod
    def save_person_or_company(
        cls, breach: Breach, person_or_company: dict[str, str], relationship: TypeOfRelationshipChoices
    ) -> "PersonOrCompany":
        """Converts a person or company dictionary into a PersonOrCompany object and saves it to the database."""
        return cls.objects.create(
            name=person_or_company.get("name", ""),
            name_of_business=(
                person_or_company["registered_company_name"]
                if person_or_company.get("do_you_know_the_registered_company_number", False)
                else person_or_company.get("name_of_business")
            ),
            website=person_or_company.get("website"),
            email=person_or_company.get("email"),
            address_line_1=person_or_company.get("address_line_1"),
            address_line_2=person_or_company.get("address_line_2"),
            address_line_3=person_or_company.get("address_line_3"),
            address_line_4=person_or_company.get("address_line_4"),
            town_or_city=person_or_company.get("town_or_city"),
            country=person_or_company.get("country"),
            county=person_or_company.get("county"),
            postal_code=person_or_company.get("postal_code", ""),
            additional_contact_details=person_or_company.get("additional_contact_details"),
            breach=breach,
            type_of_relationship=relationship,
            registered_company_number=person_or_company.get("registered_company_number"),
        )

    name = models.TextField()
    name_of_business = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.CharField(null=True, blank=True, max_length=512)
    address_line_1 = models.TextField(null=True, blank=True)
    address_line_2 = models.TextField(null=True, blank=True)
    address_line_3 = models.TextField(null=True, blank=True)
    address_line_4 = models.TextField(null=True, blank=True)
    town_or_city = models.TextField(null=True, blank=True)
    country = CountryField(blank_label="Select country")
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


class UploadedDocument(BaseModel):
    file = models.FileField(
        max_length=340,
        null=True,
        blank=True,
        # if we're storing the document in the DB, we can assume it's in the permanent bucket
        storage=PermanentDocumentStorage(),
        validators=[
            validate_virus_check_result,
        ],
    )
    breach = models.ForeignKey("Breach", on_delete=models.CASCADE, blank=False, related_name="documents")

    def file_name(self) -> str:
        return self.file.name.split("/")[-1]

    def url(self) -> str:
        return self.file.url

    @classmethod
    def save_documents(cls, breach, request) -> None:
        # Save documents
        documents = get_all_session_files(TemporaryDocumentStorage(), request.session)
        for key, _ in documents.items():
            new_key = store_document_in_permanent_bucket(object_key=key, breach_pk=breach.pk)
            UploadedDocument.objects.create(
                breach=breach,
                file=new_key,
            )


class ReporterEmailVerification(BaseModel):
    reporter_session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    email_verification_code = models.CharField(max_length=6)
    date_created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
