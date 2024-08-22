from django.db import models


class ReporterProfessionalRelationshipChoices(models.TextChoices):
    owner = "owner", "I'm an owner, officer or employee of the business, or I am the person"
    acting = "acting", "I do not work for the business or person, but I'm acting on their behalf to make a voluntary declaration"
    third_party = "third_party", "I work for a third party with a legal obligation to make a mandatory report"
    no_professional_relationship = (
        "no_professional_relationship",
        "I do not have a professional relationship with the business or person, "
        "or I no longer have a professional relationship with them",
    )


class YesNoChoices(models.TextChoices):
    yes = "yes", "Yes"
    no = "no", "No"


class YesNoDoNotKnowChoices(models.TextChoices):
    yes = "yes", "Yes"
    no = "no", "No"
    do_not_know = "do_not_know", "I do not know"


class IsTheDateAccurateChoices(models.TextChoices):
    exact = "exact", "Exact date"
    approximate = "approximate", "Approximate date"


class TypeOfRelationshipChoices(models.TextChoices):
    breacher = "breacher", "Breacher"
    supplier = "supplier", "Supplier"
    recipient = "recipient", "Recipient"
