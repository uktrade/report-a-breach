from django.apps import AppConfig
from django.conf import settings


class ReportBreachWebServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "report_a_suspected_breach"

    def ready(self) -> None:
        if settings.ENVIRONMENT == "test":
            # if we're running on a test environment, we want to override the process_email_step method, so we always use the same
            # code for testing and don't send any emails
            from config.settings.test import test_request_verify_code
            from report_a_suspected_breach.views.views_start import EmailVerifyView

            EmailVerifyView.form_valid = test_request_verify_code
