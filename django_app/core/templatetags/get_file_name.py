from django import template

register = template.Library()


@register.simple_tag
def get_file_name(key: str) -> str:
    return key.rpartition("/")[2]
