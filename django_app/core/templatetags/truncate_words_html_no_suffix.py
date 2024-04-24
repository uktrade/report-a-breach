from typing import Any

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.text import Truncator

register = Library()


@register.filter(is_safe=True)
@stringfilter
def truncate_words_html_no_suffix(value: Any, arg: int) -> str:
    """
    Truncate HTML after `arg` number of words.
    Preserve newlines in the HTML.

    Does not add the ... suffix to the truncated sentences.
    """
    try:
        length = int(arg)
    except ValueError:  # invalid literal for int()
        return value  # Fail silently.
    return Truncator(value).words(length, html=True, truncate="")
