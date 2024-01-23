from .base import *  # noqa

DEBUG = False

INSTALLED_APPS += ["django_audit_log_middleware"]

MIDDLEWARE += ["django_audit_log_middleware.AuditLogMiddleware"]
