from typing import Any

from django.conf import settings
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient
from report_a_suspected_breach.models import ReporterEmailVerification


def verify_email(reporter_email_address, request):
    verify_code = get_random_string(6, allowed_chars="0123456789")
    user_session = Session.objects.get(session_key=request.session.session_key)
    ReporterEmailVerification.objects.create(
        reporter_session=user_session,
        email_verification_code=verify_code,
    )
    print(verify_code)
    send_email(
        email=reporter_email_address,
        context={"verification_code": verify_code},
        template_id=settings.EMAIL_VERIFY_CODE_TEMPLATE_ID,
    )


def send_email(email: str, context: dict[str, Any], template_id: str, reference: str | None = None) -> HttpResponse | bool:
    """Send an email using the GOV.UK Notify API."""
    if is_whitelisted(email):
        client = NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)
        try:
            send_report = client.send_email_notification(
                email_address=email,
                template_id=template_id,
                personalisation=get_context(context),
                reference=reference,
            )
            return send_report
        except HTTPError:
            # todo - handle exceptions here
            return False
    else:
        return False


def get_context(extra_context: dict | None = None) -> dict[str, Any]:
    extra_context = extra_context or {}
    footer = "Report a trade sanctions breach service"
    context = {
        "footer": footer,
    }
    context.update(extra_context)
    return context


def is_whitelisted(email: str) -> bool:
    """
    Temporary measure to restrict notify emails to certain domains.
    disabled on production.
    """
    if settings.RESTRICT_SENDING:
        _, domain = email.split("@")
        email_domain_whitelist = (
            "gov.uk",
            "businessandtrade.gov.uk",
            "trade.gov.uk",
            "digital.trade.gov.uk",
        )
        return domain in email_domain_whitelist
    else:
        return True
