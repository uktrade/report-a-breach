from django.core.management.base import BaseCommand
from report_a_suspected_breach.models import Breach


class Command(BaseCommand):
    help = (
        "Deletes suspected breach reports when giving a list of report references. "
        "Usage: pipenv run django_app/python manage.py delete_breach_reports <reference> <reference> ..."
    )

    def add_arguments(self, parser):
        parser.add_argument("breach_references", nargs="+", type=str)

    def handle(self, *args, **options):
        for reference in options["breach_references"]:
            try:
                breach_object = Breach.objects.get(reference=reference)
                breach_object.delete()
            except Breach.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Breach {reference} does not exist"))
                continue

            self.stdout.write(self.style.SUCCESS(f"Successfully deleted breach report {reference}"))
