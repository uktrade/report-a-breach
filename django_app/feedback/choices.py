from django.db import models


class RatingChoices(models.IntegerChoices):
    VERY_DISSATISFIED = 1, "Very dissatisfied"
    DISSATISFIED = 2, "Dissatisfied"
    NEUTRAL = 3, "Neutral"
    SATISFIED = 4, "Satisfied"
    VERY_SATISFIED = 5, "Very satisfied"


class WhatDidNotWorkSoWellChoices(models.TextChoices):
    PROCESS_NOT_CLEAR = "process_not_clear", "Process is not clear"
    NOT_ENOUGH_GUIDANCE = "not_enough_guidance", "Not enough guidance"
    ASKED_FOR_INFO_I_DO_NOT_HAVE = "asked_for_info_i_do_not_have", "I was asked for information I do not have"
    COULD_NOT_FIND_THE_INFO_I_WANTED = "could_not_find_the_info_i_wanted", "I couldn't find the information I wanted"
    OTHER_ISSUE = "other_issue", "Other issue"
