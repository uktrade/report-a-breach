from django.urls import path

from .views import CompleteView

urlpatterns = [
    path("", CompleteView.as_view(), name="view_a_suspected_breach"),
    path("complete", CompleteView.as_view(), name="complete"),
]
