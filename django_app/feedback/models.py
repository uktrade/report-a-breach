from core.models import BaseModel
from django.db import models

from .choices import RatingChoices


class FeedbackItem(BaseModel):
    rating = models.IntegerField(choices=RatingChoices.choices, blank=False)
    how_we_could_improve_the_service = models.TextField(null=True, blank=True)
