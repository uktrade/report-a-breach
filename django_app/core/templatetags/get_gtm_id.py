from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_gtm_id() -> str:
    return settings.GTM_ID
