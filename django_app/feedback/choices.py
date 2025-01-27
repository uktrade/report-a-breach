from typing import List

from core.choices import BaseChoices
from django.db import models


class RatingChoices(models.IntegerChoices):
    VERY_SATISFIED = 5, "Very satisfied"
    SATISFIED = 4, "Satisfied"
    NEUTRAL = 3, "Neither satisfied nor dissatisfied"
    DISSATISFIED = 2, "Dissatisfied"
    VERY_DISSATISFIED = 1, "Very dissatisfied"


class DidYouExperienceAnyIssues(BaseChoices):
    @classmethod
    def inactive_choices(cls) -> List[str]:
        return ["no"]

    NO = "no", "I did not experience any issues"
    NOT_FOUND = "not_found", "I did not find what I was looking for"
    DIFFICULT = "difficult", "I found it difficult to navigate"
    LACKS_FEATURES = "lacks_features", "The system lacks the feature I need"
    OTHER = "other", "Other"
