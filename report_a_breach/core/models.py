import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django_chunk_upload_handlers.clam_av import validate_virus_check_result

from report_a_breach.base_classes.models import BaseModel


# This model is a WIP while we are awaiting the final schema
class BreachDetails(BaseModel):
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

    reporter_professional_relationship = models.TextField(
        null=False,
        choices=REPORTER_PROFESSIONAL_RELATIONSHIP_CHOICES,
        verbose_name="What is your professional relationship with the company or person suspected of breaching sanctions?",
    )
    reporter_email_address = models.EmailField(verbose_name="What is your email address?")
    reporter_full_name = models.TextField(verbose_name="What is your full name?")


class FileUpload(models.Model):
    # TODO: Full requirements are not yet fully defined, therefore
    # some of the code below might be changed/removed.

    # TODO: Deteremine if we need FILE_LOCATION_CHOICE.
    LOCALFILE = "local"
    S3FILE = "S3"
    FILE_LOCATION_CHOICE = [
        (LOCALFILE, "File system"),
        (S3FILE, "S3 Bucket"),
    ]
    file_location = models.CharField(
        max_length=100,
        choices=FILE_LOCATION_CHOICE,
        default=S3FILE,
    )

    s3_document_file = models.FileField(
        max_length=1000,
        null=True,
        blank=True,
        upload_to="",  # TODO: Add S3 bucket details of where file is to be stored
        validators=[
            validate_virus_check_result,
        ],
    )

    document_file_name = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
    )

    uploading_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    @property
    def file_name(self):
        return self.s3_document_file.name

    def __str__(self):
        return "{} {} {}".format(
            self.s3_document_file.name,
        )
