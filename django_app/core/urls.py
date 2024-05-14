from core.views import RedirectBaseDomainView
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", RedirectBaseDomainView.as_view(), name="initial_redirect_view"),
    path("report_a_suspected_breach/", include("report_a_suspected_breach.urls")),
    path("view_a_suspected_breach/", include("view_a_suspected_breach.urls")),
    # path("pingdom/", include("healthcheck.urls")),
    path("throw_error/", lambda x: 1 / 0),
    path("admin/", admin.site.urls),
]

if settings.ENFORCE_STAFF_SSO:
    urlpatterns.append(
        path("auth/", include("authbroker_client.urls")),
    )

if settings.ENVIRONMENT == "local":
    urlpatterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )
