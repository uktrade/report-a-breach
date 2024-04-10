from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def get_end_user_url(end_user_uuid):
    return reverse("report_a_suspected_breach_about_the_end_user", kwargs={"end_user_uuid": end_user_uuid})
