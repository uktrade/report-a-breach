from django.apps import AppConfig
from django.conf import settings


class ReportBreachWebServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "report_a_breach"

    def ready(self):

        if settings.ENVIRONMENT == "test":
            # if we're running on a test environment, we want to override the process_email_step method, so we always use the same
            # code for testing and don't send any emails
            from config.settings.test import test_process_email_step
            from report_a_breach.core.views import ReportABreachWizardView

            ReportABreachWizardView.process_email_step = test_process_email_step
