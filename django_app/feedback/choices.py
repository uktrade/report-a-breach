from django.db import models


class RatingChoices(models.IntegerChoices):
    VERY_DISSATISFIED = 1, "Very dissatisfied"
    DISSATISFIED = 2, "Dissatisfied"
    NEUTRAL = 3, "Neutral"
    SATISFIED = 4, "Satisfied"
    VERY_SATISFIED = 5, "Very satisfied"


class DidYouExperienceAnyIssues(models.TextChoices):
    NO = "no", "I did not experience any issues"
    NOT_FOUND = "not_found", "I did not find what I was looking for"
    DIFFICULT = "difficult", "I found it difficult to navigate"
    LACKS_FEATURES = "lacks_features", "The system lacks the feature I need"
    OTHER = "other", "Other"
