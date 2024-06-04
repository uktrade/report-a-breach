from django.apps import AppConfig
from django.conf import settings


class ReportBreachWebServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "report_a_suspected_breach"

    def ready(self) -> None:

        if settings.ENVIRONMENT == "test":
            # if we're running on a test environment, we want to override the process_email_step method, so we always use the same
            # code for testing and don't send any emails
            from config.settings.test import (
                test_process_email_step,
                test_request_verify_form_valid,
            )
            from report_a_suspected_breach.views import (
                ReportABreachWizardView,
                RequestVerifyCodeView,
            )

            ReportABreachWizardView.process_email_step = test_process_email_step
            RequestVerifyCodeView.form_valid = test_request_verify_form_valid
