from django.urls import include, path

urlpatterns = [
    path("", include("report_a_breach.urls")),
    path("pingdom/", include("healthcheck.urls")),
    path("throw_error/", lambda x: 1 / 0),
]
