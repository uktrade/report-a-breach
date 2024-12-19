from django.db import models


class BaseChoices(models.TextChoices):
    @classmethod
    def active_choices(cls):
        return [choice for choice in cls.choices if choice[0] not in cls.inactive_choices()]

    @classmethod
    def inactive_choices(cls):
        pass
