import logging

from core.views import (
    AccessibilityStatementView,
    CookiesConsentView,
    HelpAndSupportView,
    HideCookiesView,
    PingSessionView,
    PrivacyNoticeView,
    RedirectBaseDomainView,
    ResetSessionView,
    SessionExpiredView,
)
from django.conf import settings
from django.urls import include, path

public_urls = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("report/", include("report_a_suspected_breach.urls")),
    path("cookies-policy", CookiesConsentView.as_view(), name="cookies_consent"),
    path("hide_cookies", HideCookiesView.as_view(), name="hide_cookies"),
    path("give-feedback/", include("feedback.urls")),
    path("healthcheck/", include("healthcheck.urls")),
    path("privacy-notice", PrivacyNoticeView.as_view(), name="privacy_notice"),
    path("reset_session/", ResetSessionView.as_view(), name="reset_session"),
    path("ping_session/", PingSessionView.as_view(), name="ping_session"),
    path("report-deleted/", SessionExpiredView.as_view(), name="session_expired"),
    path("throw_error/", lambda x: 1 / 0),
    # path("download_report/", DownloadPDFView.as_view(), name="download_report"),
    path("accessibility-statement", AccessibilityStatementView.as_view(), name="accessibility_statement"),
    path("help-support", HelpAndSupportView.as_view(), name="help_and_support"),
    path("auth/", include("authbroker_client.urls")),
]

private_urls = [
    path("view/", include("view_a_suspected_breach.urls")),
]

if settings.INCLUDE_PRIVATE_URLS:
    logging.info("Include private urls")
    urlpatterns = public_urls + private_urls
else:
    logging.info("Excluding private urls")
    urlpatterns = public_urls
