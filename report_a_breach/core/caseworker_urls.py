from django.urls import path

from .views import CompleteView

urlpatterns = [
    path("", CompleteView.as_view(), name="view_a_suspected_breach"),
    path("<str:uuid>", CompleteView.as_view(), name="view_a_suspected_breach_uuid"),
]
