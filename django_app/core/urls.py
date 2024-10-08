from core.views import (
    AccessibilityStatementView,
    CookiesConsentView,
    HideCookiesView,
    PrivacyNoticeView,
    RedirectBaseDomainView,
    ResetSessionView,
)
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("report/", include("report_a_suspected_breach.urls")),
    path("view/", include("view_a_suspected_breach.urls")),
    path("cookies_consent", CookiesConsentView.as_view(), name="cookies_consent"),
    path("hide_cookies", HideCookiesView.as_view(), name="hide_cookies"),
    path("feedback/", include("feedback.urls")),
    path("healthcheck/", include("healthcheck.urls")),
    path("privacy-notice", PrivacyNoticeView.as_view(), name="privacy_notice"),
    path("reset_session/", ResetSessionView.as_view(), name="reset_session"),
    path("throw_error/", lambda x: 1 / 0),
    path("accessibility-statement", AccessibilityStatementView.as_view(), name="accessibility_statement"),
]

if settings.ENFORCE_STAFF_SSO:
    urlpatterns.append(
        path("auth/", include("authbroker_client.urls")),
    )
