from typing import Any

from authbroker_client.backends import AuthbrokerBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction


class BreachPortalAuth(AuthbrokerBackend):
    def __init__(self) -> None:
        super(BreachPortalAuth, self).__init__()

    def get_or_create_user(self, profile: dict[str, Any]) -> User:
        user_model = get_user_model()

        with transaction.atomic():
            try:
                if existing_user := User.objects.get(email=profile["email"]):
                    return existing_user
            except User.DoesNotExist:
                new_user = user_model.objects.create(
                    email=profile["email"],
                    first_name=profile["first_name"],
                    last_name=profile["last_name"],
                    username=profile["username"],
                    is_active=False,
                    is_staff=False,
                )
                new_user.set_unusable_password()
                new_user.save()

                return new_user
