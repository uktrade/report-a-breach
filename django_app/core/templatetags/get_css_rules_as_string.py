import os

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def get_css_rules_as_string(css_path):
    css_file_path = os.path.join(settings.STATIC_ROOT, css_path)
    try:
        with open(css_file_path, "r", encoding="utf-8") as reader:
            return reader.read()
    except FileNotFoundError:
        return f"{css_path} not found"
