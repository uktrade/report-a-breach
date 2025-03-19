import logging
from typing import Any

from core.base_views import BaseDownloadPDFView
from core.sites import require_view_a_breach
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, RedirectView, TemplateView
from feedback.models import FeedbackItem
from report_a_suspected_breach.models import Breach
from utils.breach_report import get_breach_context_data

from .mixins import ActiveUserRequiredMixin, StaffUserOnlyMixin

logger = logging.getLogger(__name__)


# ALL VIEWS HERE MUST BE DECORATED WITH AT LEAST LoginRequiredMixin
@method_decorator(require_view_a_breach(), name="dispatch")
class RedirectBaseViewerView(LoginRequiredMixin, ActiveUserRequiredMixin, RedirectView):
    """Redirects view_a_suspected_breach base site visits to view-all-reports view"""

    @property
    def url(self) -> str:
        return reverse("view_a_suspected_breach:summary_reports")


@method_decorator(require_view_a_breach(), name="dispatch")
class SummaryReportsView(LoginRequiredMixin, ActiveUserRequiredMixin, ListView):
    template_name = "view_a_suspected_breach/summary_reports.html"
    success_url = reverse_lazy("view_a_suspected_breach:summary_reports")

    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        self.request.session["sort"] = request.GET.get("sort_by", "newest")
        return super().get(request, **kwargs)

    def get_queryset(self) -> list[dict[str, Any]]:
        sort = self.request.session.get("sort", "newest")
        sorted_objects = []
        sorted_breaches = Breach.objects.all().order_by("-created_at")
        if sort == "oldest":
            sorted_breaches = reversed(sorted_breaches)
        for breach in sorted_breaches:
            sorted_objects.extend([get_breach_context_data(breach)])
        return sorted_objects

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["selected_sort"] = self.request.session.pop("sort", "newest")
        return context

    paginate_by = 10


@method_decorator(require_view_a_breach(), name="dispatch")
class ManageUsersView(LoginRequiredMixin, StaffUserOnlyMixin, TemplateView):
    template_name = "view_a_suspected_breach/user_admin.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pending_users"] = User.objects.filter(is_active=False, is_staff=False)
        context["accepted_users"] = User.objects.filter(is_active=True)
        return context

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        if update_user := self.request.GET.get("accept_user", None):
            user_to_accept = User.objects.get(id=update_user)
            user_to_accept.is_active = True
            user_to_accept.save()
            logger.info(f"{user_to_accept.email} has been accepted by {self.request.user.email}")
            return HttpResponseRedirect(reverse("view_a_suspected_breach:user_admin"))

        if delete_user := self.request.GET.get("delete_user", None):
            denied_user = User.objects.get(id=delete_user)
            denied_user.delete()
            logger.info(f"{denied_user.email} has been denied by {self.request.user.email}")
            return HttpResponseRedirect(reverse("view_a_suspected_breach:user_admin"))

        return super().get(request, **kwargs)


@method_decorator(require_view_a_breach(), name="dispatch")
class ViewASuspectedBreachView(LoginRequiredMixin, ActiveUserRequiredMixin, DetailView):
    template_name = "view_a_suspected_breach/view_a_suspected_breach.html"

    def get_object(self, queryset=None) -> Breach:
        self.breach = get_object_or_404(Breach, reference=self.kwargs["reference"])
        return self.breach

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["back_button_text"] = "View all suspected breach reports"
        context.update(get_breach_context_data(self.breach))
        return context


@method_decorator(require_view_a_breach(), name="dispatch")
class ViewAllFeedbackView(LoginRequiredMixin, ActiveUserRequiredMixin, ListView):
    context_object_name = "feedback"
    model = FeedbackItem
    template_name = "view_a_suspected_breach/view_all_feedback.html"

    def get_queryset(self) -> "QuerySet[FeedbackItem]":
        queryset = super().get_queryset()
        if date_min := self.request.GET.get("date_min"):
            queryset = queryset.filter(created_at__date__gte=date_min)
        if date_max := self.request.GET.get("date_max"):
            queryset = queryset.filter(created_at__date__lte=date_max)
        return queryset


@method_decorator(require_view_a_breach(), name="dispatch")
class ViewFeedbackView(LoginRequiredMixin, ActiveUserRequiredMixin, DetailView):
    model = FeedbackItem
    template_name = "view_a_suspected_breach/view_feedback.html"
    context_object_name = "feedback"


@method_decorator(require_view_a_breach(), name="dispatch")
class DownloadPDFView(LoginRequiredMixin, ActiveUserRequiredMixin, BaseDownloadPDFView):
    template_name = "view_a_suspected_breach/viewer_pdf.html"
    header = "Report a suspected breach of trade sanctions: report submitted"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        reference = self.request.GET.get("reference")
        breach_object = Breach.objects.get(reference=reference)
        context = super().get_context_data(**kwargs)
        breach_context_data = get_breach_context_data(breach_object)
        context.update(breach_context_data)
        return context
