import uuid

from django.db import models

from report_a_breach.base_classes.models import BaseModel


# This model is a WIP while we are awaiting the final schema
class BreachDetails(BaseModel):
    reporter_full_name = models.CharField(null=False)
    reporter_email_address = models.EmailField(null=False)
    reporter_professional_relationship = models.TextField(null=False)
