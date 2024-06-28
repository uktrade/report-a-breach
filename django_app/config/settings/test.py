from typing import Any

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.dummy import DummyCache
from django.forms import Form
from django.http import HttpResponse

from .base import *  # noqa

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = True

BASE_FRONTEND_TESTING_URL = "http://report-a-suspected-breach:8000"

ENVIRONMENT = "test"

# we don't want to connect to ClamAV in testing, redefine and remove from list
FILE_UPLOAD_HANDLERS = ("core.custom_upload_handler.CustomFileUploadHandler",)  # Order is important


# don't use redis when testing
class TestingCache(DummyCache):
    """A dummy cache that implements the same interface as the django-redis cache."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dict_cache = {}

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        if key in self.dict_cache:
            return False
        self.dict_cache[key] = value
        return True

    def get(self, key, *args, **kwargs):
        return self.dict_cache.get(key)

    def set(self, key, value, **kwargs):
        self.dict_cache[key] = value

    def iter_keys(self, *args, search="", **kwargs):
        for key in self.dict_cache.keys():
            if search in key:
                yield key

    def clear(self):
        self.dict_cache = {}


CACHES = {"default": {"BACKEND": "config.settings.test.TestingCache"}}


def test_process_email_step(self, form: Form) -> dict[str, Any]:
    """Monkey-patching the process_email_step of the wizard to always use the same verify code for testing."""
    from django.contrib.sessions.models import Session
    from report_a_suspected_breach.models import ReporterEmailVerification

    verify_code = "012345"
    user_session = Session.objects.get(session_key=self.request.session.session_key)
    ReporterEmailVerification.objects.create(
        reporter_session=user_session,
        email_verification_code=verify_code,
    )
    print(verify_code)
    return self.get_form_step_data(form)


def test_request_verify_form_valid(self, form: Form) -> HttpResponse:
    """Monkey-patching the form_valid of the request verify code view to always use the same verify code for testing."""
    import logging

    from django.contrib.sessions.models import Session
    from report_a_suspected_breach.models import ReporterEmailVerification
    from report_a_suspected_breach.views import RequestVerifyCodeView

    logger = logging.getLogger(__name__)

    reporter_email_address = self.request.session["reporter_email_address"]

    verify_code = "987654"
    user_session = Session.objects.get(session_key=self.request.session.session_key)
    if getattr(self.request, "limited", False):
        logger.warning(f"User has been rate-limited: {reporter_email_address}")
        return self.form_invalid(form)
    ReporterEmailVerification.objects.create(
        reporter_session=user_session,
        email_verification_code=verify_code,
    )
    print(verify_code)
    return super(RequestVerifyCodeView, self).form_valid(form)
