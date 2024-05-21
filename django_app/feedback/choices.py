from django.db import models


class RatingChoices(models.IntegerChoices):
    VERY_DISSATISFIED = 1, "Very dissatisfied"
    DISSATISFIED = 2, "Dissatisfied"
    NEUTRAL = 3, "Neutral"
    SATISFIED = 4, "Satisfied"
    VERY_SATISFIED = 5, "Very satisfied"
