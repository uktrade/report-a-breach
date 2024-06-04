from typing import Any

from django.core.cache.backends.dummy import DummyCache
from django.forms import Form

from .base import *  # noqa

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = True

BASE_FRONTEND_TESTING_URL = "http://report-a-suspected-breach:8000"

ENVIRONMENT = "test"

# we don't want to connect to ClamAV in testing, redefine and remove from list
FILE_UPLOAD_HANDLERS = ("django_chunk_upload_handlers.s3.S3FileUploadHandler",)  # Order is important


# don't use redis when testing
class TestingCache(DummyCache):
    """A dummy cache that implements the same interface as the django-redis cache."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dict_cache = {}

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
