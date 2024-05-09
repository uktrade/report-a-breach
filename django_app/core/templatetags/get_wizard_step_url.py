from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def get_wizard_step_url(step_name: str) -> str:
    from report_a_suspected_breach.urls import report_a_suspected_breach_wizard

    return reverse(report_a_suspected_breach_wizard.view_initkwargs["url_name"], kwargs={"step": step_name})
