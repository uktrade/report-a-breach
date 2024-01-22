from django.urls import path, include

urlpatterns = [
    path("", include("report_a_breach.core.urls")),
]
