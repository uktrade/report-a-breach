from django.urls import path

from . import views

app_name = "view_a_suspected_breach"

urlpatterns = [
    path("", views.ViewABreachView.as_view(), name="landing"),
    path("files", views.FileFieldFormView.as_view(), name="files"),
]
