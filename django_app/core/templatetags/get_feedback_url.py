import urllib.parse

from django import template
from django.http import HttpRequest

register = template.Library()


@register.simple_tag
def get_feedback_url(request: HttpRequest) -> str:
    request_url = request.scheme + "://" + request.META["HTTP_HOST"] + request.path
    return urllib.parse.quote(request_url)
