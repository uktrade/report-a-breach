from django import template
from django.conf import settings

register = template.Library()


# settings value
@register.simple_tag
def gtm_enabled() -> bool:
    return settings.GTM_ENABLED and settings.GTM_ID
