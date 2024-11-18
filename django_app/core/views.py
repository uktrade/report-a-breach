from typing import Any

from core.sites import (
    is_report_a_suspected_breach_site,
    is_view_a_suspected_breach_site,
)
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import FormView, RedirectView, TemplateView
from django_ratelimit.exceptions import Ratelimited
from playwright.sync_api import sync_playwright

from .forms import CookiesConsentForm, HideCookiesForm
from .utils import update_last_activity_session_timestamp


class RedirectBaseDomainView(RedirectView):
    """Redirects base url visits to either report a breach app or view app default view"""

    @property
    def url(self) -> str:
        if is_report_a_suspected_breach_site(self.request.site):
            return reverse("report_a_suspected_breach:tasklist")
        elif is_view_a_suspected_breach_site(self.request.site):
            return reverse("view_a_suspected_breach:summary_reports")
        return ""


class CookiesConsentView(FormView):
    template_name = "core/cookies_consent.html"
    form_class = CookiesConsentForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        initial_dict = {}

        if current_cookies_policy := self.request.COOKIES.get("accepted_ga_cookies"):
            initial_dict["accept_cookies"] = current_cookies_policy == "true"
            kwargs["initial"] = initial_dict

        # redirect the user back to the page they were on before they were shown the cookie consent form
        if redirect_back_to := self.request.GET.get("redirect_back_to"):
            self.request.session["redirect_back_to"] = redirect_back_to

        return kwargs

    def form_valid(self, form: CookiesConsentForm) -> HttpResponse:
        # cookie consent lasts for 1 year
        cookie_max_age = 365 * 24 * 60 * 60

        if "came_from_cookies_page" in self.request.GET:
            response = redirect(reverse("cookies_consent") + "?cookies_set=true")
        else:
            response = redirect(self.request.session.get("redirect_back_to", "/") + "?cookies_set=true")

        # regardless of their choice, we set a cookie to say they've made a choice
        response.set_cookie("cookie_preferences_set", "true", max_age=cookie_max_age)
        response.set_cookie(
            "accepted_ga_cookies",
            "true" if form.cleaned_data["do_you_want_to_accept_analytics_cookies"] else "false",
            max_age=cookie_max_age,
        )
        return response


class HideCookiesView(FormView):
    template_name = "core/hide_cookies.html"
    form_class = HideCookiesForm

    def form_valid(self, form: HideCookiesForm) -> HttpResponse:
        referrer_url = self.request.GET.get("redirect_back_to", "/")
        return redirect(referrer_url)


def rate_limited_view(request: HttpRequest, exception: Ratelimited) -> HttpResponse:
    return HttpResponse("You have made too many", status=429)


class ResetSessionView(View):
    """Resets and clears the users session"""

    def get(self, request: HttpRequest) -> HttpResponse:
        request.session.flush()
        return redirect("initial_redirect_view")


class PrivacyNoticeView(TemplateView):
    template_name = "core/privacy_notice.html"


class AccessibilityStatementView(TemplateView):
    template_name = "core/accessibility_statement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["otsi_email"] = settings.OTSI_EMAIL
        return context


class PingSessionView(View):
    """Pings the session to keep it alive"""

    def get(self, request: HttpRequest) -> HttpResponse:
        update_last_activity_session_timestamp(request)
        return HttpResponse("pong")


class SessionExpiredView(TemplateView):
    template_name = "core/session_expired.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        # the session should already be empty by definition but just in case, manually clear
        request.session.flush()
        return super().get(request, *args, **kwargs)


class DownloadPDFView(TemplateView):
    # TODO: update the template when DST-797 is complete
    template_name = "core/report_pdf.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context_data = self.get_context_data()
        filename = f"report-{context_data['reference']}.pdf"
        pdf_data = None
        template_string = render_to_string(self.template_name, context=context_data)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(mark_safe(template_string))
            pdf_data = page.pdf(format="A4")
            browser.close()

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={filename}"

        return response

    def get_context_data(self, *args: object, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["reference"] = self.request.GET.get("reference", "")
        return context
