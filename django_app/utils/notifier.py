from django.conf import settings
from notifications_python_client.errors import HTTPError
from notifications_python_client.notifications import NotificationsAPIClient


def send_email(email, context, template_id, reference=None) -> dict | bool:
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


def get_context(extra_context=None):
    extra_context = extra_context or {}
    footer = "Report a trade sanctions breach service"
    context = {
        "footer": footer,
    }
    context.update(extra_context)
    return context


def is_whitelisted(email):
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
