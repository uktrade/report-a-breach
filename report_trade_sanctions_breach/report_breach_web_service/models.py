import uuid

from django.db import models


# Create your models here.
class BreachDetails(models.Model):
    # might not be needed, as django can auto create a primary key
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # most likely redundant as the json will hold date data
    report_date = models.DateField(auto_now=True)
    # TODO: add auto json validation - separate ticket, on hold for data model
    data = models.JSONField(default=dict)