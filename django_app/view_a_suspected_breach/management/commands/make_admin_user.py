from typing import Dict

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Create the admin user for View a Suspected Breach"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--emails",
            nargs="*",
            help="list of emails to make admin user",
            default=[],
            type=str,
        )

    def handle(self, *args: object, **options: Dict[str, list[str]]) -> None:
        emails = options["emails"]

        user_objects = User.objects.all()
        for email in emails:
            try:
                existing_user = user_objects.get(email=email)
                existing_user.is_staff = True
                existing_user.is_active = True
                existing_user.save()
                self.stdout.write(self.style.SUCCESS("User updated successfully"))

            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR("User does not exist"))
