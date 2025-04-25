from config.env import env
from config.settings.deploy.base import *  # noqa

DEBUG = False

ENVIRONMENT = "production"

# Django extra production sites
REPORT_A_SUSPECTED_BREACH_EXTRA_DOMAIN = env.report_a_suspected_breach_extra_domain
VIEW_A_SUSPECTED_BREACH_EXTRA_DOMAIN = env.view_a_suspected_breach_extra_domain
REPORT_A_SUSPECTED_BREACH_SERVICE_DOMAIN = env.report_a_suspected_breach_service_domain
VIEW_A_SUSPECTED_BREACH_SERVICE_DOMAIN = env.view_a_suspected_breach_service_domain
