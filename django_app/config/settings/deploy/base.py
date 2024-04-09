"""Configuration settings for deployment to all environments."""

from config.settings.base import *  # noqa
from django_log_formatter_asim import ASIMFormatter

INSTALLED_APPS += ["django_audit_log_middleware"]

MIDDLEWARE += ["django_audit_log_middleware.AuditLogMiddleware"]

LOGGING = {
    "formatters": {
        "ecs_formatter": {
            "()": ASIMFormatter,
        },
    },
    "handlers": {
        "ecs": {
            "formatter": "ecs_formatter",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["ecs"],
        },
    },
    "version": 1,
}
