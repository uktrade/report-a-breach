from core.views import (
    CookiesConsentView,
    HideCookiesView,
    RedirectBaseDomainView,
    ResetSessionView,
)
from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("report_a_suspected_breach/", include("report_a_suspected_breach.urls")),
    path("view_a_suspected_breach/", include("view_a_suspected_breach.urls")),
    path("cookies_consent", CookiesConsentView.as_view(), name="cookies_consent"),
    path("hide_cookies", HideCookiesView.as_view(), name="hide_cookies"),
    path("feedback/", include("feedback.urls")),
    path("pingdom/", include("healthcheck.urls")),
    path("reset_session/", ResetSessionView.as_view(), name="reset_session"),
    path("throw_error/", lambda x: 1 / 0),
]

if settings.ENFORCE_STAFF_SSO:
    urlpatterns.append(
        path("auth/", include("authbroker_client.urls")),
    )
