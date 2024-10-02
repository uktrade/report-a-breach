from django.urls import path

from .views import HealthCheckView

app_name = "healthcheck"

urlpatterns = [
    path("", HealthCheckView.as_view(), name="healthcheck_ping"),
    path("ping.xml", HealthCheckView.as_view(), name="healthcheck_ping"),
]
