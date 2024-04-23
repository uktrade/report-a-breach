from django.conf import settings


def truncate_words_limit(request):
    return {
        "truncate_words_limit": settings.TRUNCATE_WORDS_LIMIT,
    }
