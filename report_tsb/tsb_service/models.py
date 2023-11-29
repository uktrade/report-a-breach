from django.db import models


# Create your models here.
class BreachDetails(models.Model):
    report_date = models.DateField(auto_now=True)
    data = models.JSONField(default="dict")
