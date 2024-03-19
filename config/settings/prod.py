from django_log_formatter_ecs import ECSFormatter

from .base import *  # noqa

DEBUG = False

INSTALLED_APPS += ["django_audit_log_middleware"]

MIDDLEWARE += ["django_audit_log_middleware.AuditLogMiddleware"]

LOGGING = {
    "formatters": {
        "ecs_formatter": {
            "()": ECSFormatter,
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

ENVIRONMENT = "production"
