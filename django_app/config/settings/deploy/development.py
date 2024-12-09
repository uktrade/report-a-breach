import sys

from config.asim_formatter import DDASIMFormatter
from config.settings.deploy.base import *  # noqa

ENVIRONMENT = "development"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # Define the custom ASIM formatter (see above)
        "asim_formatter": {
            "()": DDASIMFormatter,
        },
    },
    "handlers": {
        "asim": {
            "class": "logging.StreamHandler",
            "formatter": "asim_formatter",
            "filters": ["request_id_context"],
        },
        "stdout": {  # This ensures that logs from non-application code are formatted
            "class": "logging.StreamHandler",
            "formatter": "asim_formatter",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["stdout"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": [
                "asim",
            ],
            "level": "DEBUG",
            # Python's logging system is hierarchical.
            # This prevents duplicate log messages that would result from
            #  allowing messages to propagate to higher-level loggers.
            "propagate": False,
        },
        "django.request": {
            "handlers": [
                "asim",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
        "requestlogs": {
            "handlers": [
                "asim",
            ],
            "level": "INFO",
            "propagate": False,
        },
        # The Datadog trace agent sends its own log messages via this
        #  named logger. Explicitly specifying the handler here
        #  ensures that they are also in ASIM format.
        "ddtrace": {
            "handlers": ["asim"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "filters": {
        "request_id_context": {
            "()": "requestlogs.logging.RequestIdContext",
        },
    },
}
