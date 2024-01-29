import re

from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient


def get_client():
    """
    Return a Notification client
    """
    return NotificationsAPIClient(settings.GOV_NOTIFY_API_KEY)


def send_mail(email, context, template_id, reference=None):
    if is_whitelisted(email):
        client = get_client()
        send_report = client.send_email_notification(
            email_address=email,
            template_id=template_id,
            personalisation=get_context(context),
            reference=reference,
        )
    else:
        send_report = {
            "content": {},
            "whitelist": False,
        }
    send_report["to_email"] = email
    send_report["template_id"] = template_id
    return send_report


def get_context(extra_context=None):
    extra_context = extra_context or {}
    footer = "Report a trade sanctions breach service"
    context = {
        "footer": footer,
    }
    context.update(extra_context)
    return context


def get_template(template_id):
    client = get_client()
    return client.get_template(template_id)


def get_preview(template_id, values):
    client = get_client()
    return client.post_template_preview(
        template_id=template_id, personalisation=get_context(values)
    )


def is_whitelisted(email):
    """
    Temporary measure to restrict notify emails to certain domains.
    disabled on production.
    """
    # if (
    #     os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith("prod")
    #     or settings.DISABLE_NOTIFY_WHITELIST
    # ):
    #     return True

    whitelist = {"gov.uk", "businessandtrade.gov.uk", "trade.gov.uk", "digital.trade.gov.uk"}
    regex_whitelist = []
    _, domain = email.split("@")
    in_whitelist = domain in whitelist or email in whitelist
    if not in_whitelist:
        in_whitelist = any([re.match(pattern, email) for pattern in regex_whitelist])
    return in_whitelist
