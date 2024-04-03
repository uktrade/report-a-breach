from .base import *  # noqa

TEST_EMAIL_VERIFY_CODE = True

HEADLESS = env.bool("HEADLESS", default=True)

BASE_FRONTEND_TESTING_URL = env.str("BASE_FRONTEND_TESTING_URL", default="http://localhost:8000")

ENVIRONMENT = "test"


def test_process_email_step(self, form):
    """Monkey-patching the process_email_step of the wizard to always use the same verify code for testing."""
    from django.contrib.sessions.models import Session

    from report_a_breach.core.models import ReporterEmailVerification

    verify_code = "012345"
    user_session = Session.objects.get(session_key=self.request.session.session_key)
    ReporterEmailVerification.objects.create(
        reporter_session=user_session,
        email_verification_code=verify_code,
    )
    print(verify_code)
    return self.get_form_step_data(form)
