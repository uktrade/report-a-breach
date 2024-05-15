from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("", views.ProvideFullFeedbackView.as_view(), name="collect_full_feedback"),
    path("<uuid:existing_feedback_id>", views.ProvideFullFeedbackView.as_view(), name="amend_feedback"),
    path("collect_feedback", views.ProvidePartialFeedbackView.as_view(), name="collect_feedback"),
    path("done", views.FeedbackDoneView.as_view(), name="feedback_done"),
]
