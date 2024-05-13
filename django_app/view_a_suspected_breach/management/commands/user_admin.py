from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the admin user for View a Suspected Breach"

    def add_arguments(self, parser):
        parser.add_argument("--first_name", type=str)
        parser.add_argument("--last_name", type=str)
        parser.add_argument("--email", type=str)

    def handle(self, *args, **options):
        first_name, last_name, email = options["first_name"], options["last_name"], options["email"]

        user_objects = User.objects.all()
        if existing_user := user_objects.get(email=email):
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            existing_user.is_staff = True
            existing_user.is_active = False
            existing_user.save()

        else:
            User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_staff=True,
                is_active=False,
            )
        self.stdout.write(self.style.SUCCESS("User Added Successfully"))
