from django.urls import path

from .views import HealthCheckView

urlpatterns = [
    path("", HealthCheckView.as_view()),
]
