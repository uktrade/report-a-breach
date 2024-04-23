from typing import Any, Dict

from django.conf import settings
from django.http import HttpRequest


def truncate_words_limit(request: HttpRequest) -> Dict[str, Any]:
    return {
        "truncate_words_limit": settings.TRUNCATE_WORDS_LIMIT,
    }
