from core.views import (
    AccessibilityStatementView,
    CookiesConsentView,
    DownloadPDFView,
    HideCookiesView,
    PingSessionView,
    PrivacyNoticeView,
    RedirectBaseDomainView,
    ResetSessionView,
    SessionExpiredView,
)
from django.urls import include, path

urlpatterns = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("report/", include("report_a_suspected_breach.urls")),
    path("view/", include("view_a_suspected_breach.urls")),
    path("cookies-policy", CookiesConsentView.as_view(), name="cookies_consent"),
    path("hide_cookies", HideCookiesView.as_view(), name="hide_cookies"),
    path("feedback/", include("feedback.urls")),
    path("healthcheck/", include("healthcheck.urls")),
    path("privacy-notice", PrivacyNoticeView.as_view(), name="privacy_notice"),
    path("reset_session/", ResetSessionView.as_view(), name="reset_session"),
    path("ping_session/", PingSessionView.as_view(), name="ping_session"),
    path("session_expired/", SessionExpiredView.as_view(), name="session_expired"),
    path("throw_error/", lambda x: 1 / 0),
    path("download_application/", DownloadPDFView.as_view(), name="download_application"),
    path("accessibility-statement", AccessibilityStatementView.as_view(), name="accessibility_statement"),
    path("auth/", include("authbroker_client.urls")),
]
