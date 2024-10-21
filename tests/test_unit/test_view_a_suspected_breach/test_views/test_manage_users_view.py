import logging

import pytest
from django.contrib.auth.models import User
from django.urls import reverse


def test_approve_user(vasb_client, caplog):
    test_user = User.objects.create_user(username="John", email="john@example.com", is_active=False)
    admin_user = User.objects.create_user(
        username="Jane", email="jane@example.com", is_staff=True, is_active=True, is_superuser=True
    )
    vasb_client.force_login(admin_user)

    with caplog.at_level(logging.INFO):
        vasb_client.get(reverse("view_a_suspected_breach:user_admin") + f"?accept_user={test_user.id}")
        test_user.refresh_from_db()
        assert test_user.is_active

        # test logging
        assert "john@example.com has been accepted by jane@example.com" in caplog.text


def test_deny_user(vasb_client, caplog):
    test_user = User.objects.create_user(username="John", email="john@example.com", is_active=False)
    admin_user = User.objects.create_user(
        username="Jane", email="jane@example.com", is_staff=True, is_active=True, is_superuser=True
    )
    vasb_client.force_login(admin_user)

    with caplog.at_level(logging.INFO):
        vasb_client.get(reverse("view_a_suspected_breach:user_admin") + f"?delete_user={test_user.id}")

        with pytest.raises(User.DoesNotExist):
            test_user.refresh_from_db()

        # test logging
        assert "john@example.com has been denied by jane@example.com" in caplog.text
