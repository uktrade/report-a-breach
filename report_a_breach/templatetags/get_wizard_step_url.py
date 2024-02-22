from django import template
from django.urls import reverse

from report_a_breach.core.urls import report_a_breach_wizard

register = template.Library()


@register.simple_tag
def get_wizard_step_url(step_name):
    return reverse(report_a_breach_wizard.view_initkwargs["url_name"], kwargs={"step": step_name})
