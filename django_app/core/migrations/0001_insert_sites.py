from django.db import migrations
from django.conf import settings


def insert_sites(apps, schema_editor):
    """Populate the sites model"""
    Site = apps.get_model("sites", "Site")
    Site.objects.all().delete()

    # Register SITE_ID = 1
    Site.objects.create(domain=settings.REPORT_A_SUSPECTED_BREACH_DOMAIN, name="report-a-suspected-breach")
    # Register SITE_ID = 2
    Site.objects.create(domain=settings.VIEW_A_SUSPECTED_BREACH_DOMAIN, name="view-a-suspected-breach")


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [migrations.RunPython(insert_sites)]
