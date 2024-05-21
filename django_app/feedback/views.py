import logging
from typing import Any

from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, TemplateView

from .forms import FeedbackForm
from .models import FeedbackItem

logger = logging.getLogger(__name__)


class ProvideFullFeedbackView(FormView):
    """View for collecting full feedback from the user."""

    form_class = FeedbackForm
    template_name = "feedback/collect_feedback.html"

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if existing_feedback_id := self.kwargs.get("existing_feedback_id"):
            kwargs["instance"] = get_object_or_404(FeedbackItem, id=existing_feedback_id)
        return kwargs

    def form_valid(self, form: FeedbackForm) -> HttpResponseRedirect:
        form.save()
        return redirect("feedback:feedback_done")


class FeedbackDoneView(TemplateView):
    template_name = "feedback/feedback_done.html"
