from unittest.mock import patch

from django.test import override_settings
from notifications_python_client.errors import HTTPError
from utils.notifier import send_email


@override_settings(GOV_NOTIFY_API_KEY="test_key")
def test_send_email():
    send_email(
        email="test@example.com", context={"verification_code": "123456"}, template_id="123456", reference="test_reference"
    )
    from utils.notifier import NotificationsAPIClient

    NotificationsAPIClient.assert_called_once_with("test_key")
    assert NotificationsAPIClient.return_value.send_email_notification.call_count == 1
    NotificationsAPIClient.return_value.send_email_notification.assert_called_once_with(
        email_address="test@example.com",
        personalisation={"verification_code": "123456", "footer": "Report a trade sanctions breach service"},
        template_id="123456",
        reference="test_reference",
    )


def test_failure_to_send_email():
    from utils.notifier import NotificationsAPIClient

    NotificationsAPIClient.return_value.send_email_notification.side_effect = HTTPError()

    with patch("utils.notifier.sentry_sdk", autospec=True) as patched_sentry_sdk:
        response = send_email(
            email="test@example.com",
            context={"verification_code": "123456"},
            template_id="123456",
            reference="test_reference",
        )
        assert response is False
        assert patched_sentry_sdk.capture_exception.call_count == 1
