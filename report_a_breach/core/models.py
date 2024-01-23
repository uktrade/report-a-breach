import uuid

from django.db import models

from report_a_breach.base_classes.models import BaseModel


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
