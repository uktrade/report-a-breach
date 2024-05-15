from core.models import BaseModel
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .choices import RatingChoices, WhatDidNotWorkSoWellChoices


class FeedbackItem(BaseModel):
    rating = models.IntegerField(choices=RatingChoices.choices, blank=False)
    what_did_not_work_so_well = ArrayField(
        base_field=models.CharField(max_length=32, choices=WhatDidNotWorkSoWellChoices.choices), blank=True, null=True
    )
    how_we_could_improve_the_service = models.TextField(null=True, blank=True)
