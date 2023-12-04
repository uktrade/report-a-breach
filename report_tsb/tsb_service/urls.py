from django.urls import path

from .views import StartView

urlpatterns = [
    path("", StartView.as_view(), name="index"),
]
