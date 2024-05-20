import uuid

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    help = "Create the admin user for View a Suspected Breach"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--first_name", type=str)
        parser.add_argument("--last_name", type=str)
        parser.add_argument("--email", type=str)

    def handle(self, *args: object, **options: object) -> None:
        first_name, last_name, email = options["first_name"], options["last_name"], options["email"]

        user_objects = User.objects.all()
        password = str(uuid.uuid4())
        unique_str = str(uuid.uuid4())
        username = f"{last_name}_{unique_str}"
        try:
            existing_user = user_objects.get(email=email)
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            existing_user.is_staff = True
            existing_user.is_active = True
            existing_user.username = username
            existing_user.password = password
            existing_user.save()
            self.stdout.write(self.style.SUCCESS("User updated successfully"))

        except User.DoesNotExist:
            User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_staff=True,
                is_active=True,
                username=username,
                password=password,
            )
            self.stdout.write(self.style.SUCCESS("User added successfully"))
