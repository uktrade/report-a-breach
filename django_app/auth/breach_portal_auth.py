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
        id_key = self.get_profile_id_name()

        with transaction.atomic():
            if existing_user := user_model.objects.filter(email=profile["email"]):
                if existing_user[0]:
                    if existing_user[0].is_staff:
                        return existing_user
            else:
                user, created = user_model.objects.get_or_create(
                    **{user_model.USERNAME_FIELD: profile[id_key]},
                    defaults=self.user_create_mapping(profile),
                )

                if created:
                    user.set_unusable_password()
                    user.is_active = False
                    user.is_staff = False
                    user.save()

        return user

    def user_create_mapping(self, profile: dict[str, Any]) -> dict[str, Any]:
        return {
            "email": profile["email"],
            "first_name": profile["first_name"],
            "last_name": profile["last_name"],
            "is_active": False,
            "is_staff": False,
        }
