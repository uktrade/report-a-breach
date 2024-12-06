from typing import Any

from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.dummy import DummyCache
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.forms import Form
from django.http import HttpResponse

from .base import *  # noqa

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = False

BASE_FRONTEND_TESTING_URL = "http://report-a-suspected-breach:8000"

SAVE_VIDEOS = False

ENVIRONMENT = "test"


class TestUploadHandler(TemporaryFileUploadHandler):
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file.original_name = self.file_name


# we don't want to connect to ClamAV in testing, redefine and remove from list
FILE_UPLOAD_HANDLERS = ("config.settings.test.TestUploadHandler",)


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
    """Monkey-patching the process_email_step of the journey to always use the same verify code for testing."""
    from django.contrib.sessions.models import Session
    from report_a_suspected_breach.models import ReporterEmailVerification

    verify_code = "012345"
    user_session = Session.objects.get(session_key=self.request.session.session_key)
    ReporterEmailVerification.objects.create(
        reporter_session=user_session,
        email_verification_code=verify_code,
    )
    return self.get_form_step_data(form)


def test_request_verify_code(self, form: Form) -> HttpResponse:
    """Monkey-patching the form_valid of the request verify code view to always use the same verify code for testing."""

    from django.contrib.sessions.models import Session
    from report_a_suspected_breach.models import ReporterEmailVerification
    from report_a_suspected_breach.views.views_start import EmailVerifyView

    verify_code = "012345"
    user_session = Session.objects.get(session_key=self.request.session.session_key)
    ReporterEmailVerification.objects.create(
        reporter_session=user_session,
        email_verification_code=verify_code,
    )

    return super(EmailVerifyView, self).form_valid(form)
