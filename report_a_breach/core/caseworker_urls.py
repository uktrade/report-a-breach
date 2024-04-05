from django.urls import path

from .views import ViewABreachView

urlpatterns = [
    path("", ViewABreachView.as_view(), name="view_a_suspected_breach"),
    path("<str:uuid>", ViewABreachView.as_view(), name="view_a_suspected_breach_uuid"),
]
