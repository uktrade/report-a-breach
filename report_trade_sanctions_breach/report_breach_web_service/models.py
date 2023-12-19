import uuid

from django.db import models


# This model is a WIP while we are awaiting the final schema
class BreachDetails(models.Model):
    # might not be needed, as django can auto create a primary key
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter_full_name = models.CharField(blank=True, null=True)
    reporter_professional_relationship = models.TextField(blank=True, null=True)
    reporter_confirmation_id = models.CharField(blank=True, null=True)
