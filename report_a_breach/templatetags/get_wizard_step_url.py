from django import template

from report_a_breach.core.urls import report_a_breach_wizard

register = template.Library()


@register.filter
def get_wizard_step_url(step_name):
    return report_a_breach_wizard.get_step_url(step_name)
