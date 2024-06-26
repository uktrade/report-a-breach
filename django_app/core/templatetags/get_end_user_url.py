from django import template
from django.http import HttpResponse
from django.urls import reverse

register = template.Library()


@register.simple_tag
def get_end_user_url(end_user_uuid: str) -> HttpResponse:
    return reverse("report_a_suspected_breach:about_the_end_user", kwargs={"end_user_uuid": end_user_uuid})
