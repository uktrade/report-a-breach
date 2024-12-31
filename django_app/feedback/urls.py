from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("", views.ProvideFullFeedbackView.as_view(), name="collect_full_feedback"),
    path("done", views.FeedbackDoneView.as_view(), name="feedback_done"),
]
