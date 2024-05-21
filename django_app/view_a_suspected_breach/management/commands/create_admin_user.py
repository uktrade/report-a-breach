from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Create the admin user for View a Suspected Breach"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--email", type=str)

    def handle(self, *args: object, **options: object) -> None:
        email = options["email"]

        user_objects = User.objects.all()
        try:
            existing_user = user_objects.get(email=email)
            existing_user.is_staff = True
            existing_user.is_active = True
            existing_user.save()
            self.stdout.write(self.style.SUCCESS("User updated successfully"))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User does not exist"))
