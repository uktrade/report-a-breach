from django.urls import path

from .views import HealthCheckView

urlpatterns = [
    path("ping.xml", HealthCheckView.as_view()),
]
