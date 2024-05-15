import logging
from typing import Any

from core.utils import is_ajax
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .forms import FeedbackForm
from .models import FeedbackItem

logger = logging.getLogger(__name__)


class ProvidePartialFeedbackView(FormView):
    """View for collecting partial feedback from the user, i.e. just the rating."""

    template_name = "feedback/collect_feedback.html"
    form_class = FeedbackForm
    http_method_names = ["post"]

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        if existing_feedback_id := self.request.POST.get("existing_feedback_id"):
            kwargs["instance"] = get_object_or_404(FeedbackItem, id=existing_feedback_id)
        return kwargs

    def form_valid(self, form: FeedbackForm) -> JsonResponse | HttpResponseRedirect:
        feedback = form.save()
        if is_ajax(self.request):
            return JsonResponse(
                {
                    "success": True,
                    "second_step_url": reverse("feedback:amend_feedback", kwargs={"existing_feedback_id": feedback.id}),
                    "feedback_id": str(feedback.id),
                }
            )
        else:
            # redirect the user to the full feedback form
            return redirect("feedback:amend_feedback", existing_feedback_id=feedback.id)

    def form_invalid(self, form: FeedbackForm) -> JsonResponse:
        return JsonResponse(
            {
                "success": False,
                "errors": form.errors,
            },
            status=400,
        )


class ProvideFullFeedbackView(FormView):
    """View for collecting full feedback from the user, including all questions."""

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

    def form_invalid(self, form: FeedbackForm) -> HttpResponseRedirect:
        """We want to mock the form submission as successful even if it's invalid.

        The form should never be invalid so if it is, there's been a bug. Let's log the bug for debugging purposes."""

        logger.error("Feedback form is invalid", extra={"form_errors": form.errors})
        return redirect("feedback:feedback_done")


class FeedbackDoneView(TemplateView):
    template_name = "feedback/feedback_done.html"
