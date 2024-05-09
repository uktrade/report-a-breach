from typing import Any

from authbroker_client.backends import AuthbrokerBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class BreachPortalAuth(AuthbrokerBackend):
    def __init__(self) -> None:
        super(BreachPortalAuth, self).__init__()

    def get_or_create_user(self, profile: dict[str, Any]) -> User:
        user_model = get_user_model()
        id_key = self.get_profile_id_name()

        user, created = user_model.objects.get_or_create(
            **{user_model.USERNAME_FIELD: profile[id_key]},
            defaults=self.user_create_mapping(profile),
        )

        if created:
            user.set_unusable_password()
            user.is_active = True
            user.is_staff = False
            user.save()
        return user
