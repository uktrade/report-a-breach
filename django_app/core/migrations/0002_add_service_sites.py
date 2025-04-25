from django.conf import settings
from django.db import migrations


def insert_sites(apps, schema_editor):
    """Populate the sites model"""
    Site = apps.get_model("sites", "Site")
    Site.objects.all().delete()

    if settings.ENVIRONMENT == "production":
        # Register SITE_ID = 5
        Site.objects.create(domain=settings.REPORT_A_SUSPECTED_BREACH_SERVICE_DOMAIN, name="report-a-suspected-breach")
        # Register SITE_ID = 6
        Site.objects.create(domain=settings.VIEW_A_SUSPECTED_BREACH_SERVICE_DOMAIN, name="view-a-suspected-breach")


def remove_sites(apps, schema_editor):
    """Populate the sites model"""
    Site = apps.get_model("sites", "Site")
    if settings.ENVIRONMENT == "production":
        Site.objects.filter(domain=settings.REPORT_A_SUSPECTED_BREACH_SERVICE_DOMAIN).delete()
        Site.objects.filter(domain=settings.VIEW_A_SUSPECTED_BREACH_SERVICE_DOMAIN).delete()


class Migration(migrations.Migration):
    dependencies = [("sites", "0001_insert_sites")]
    operations = [migrations.RunPython(insert_sites, reverse_code=remove_sites)]
