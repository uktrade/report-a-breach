# Generated by Django 4.2.10 on 2024-02-27 12:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("report_a_breach", "0002_alter_breach_sanctions_regimes_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalsanctionsregimebreachthrough",
            name="unknown_regime",
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name="sanctionsregimebreachthrough",
            name="unknown_regime",
            field=models.BooleanField(null=True),
        ),
    ]