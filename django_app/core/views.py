# from collections import OrderedDict
from typing import Any

# import ring
from core.sites import (
    is_report_a_suspected_breach_site,
    is_view_a_suspected_breach_site,
)
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, RedirectView
from django_ratelimit.exceptions import Ratelimited

from .forms import CookiesConsentForm, HideCookiesForm


class BaseFormView(FormView):
    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        if form_h1_header := getattr(form, "form_h1_header", None):
            context["form_h1_header"] = form_h1_header
        return context


class RedirectBaseDomainView(RedirectView):
    """Redirects base url visits to either report a breach app or view app default view"""

    @property
    def url(self) -> str:
        if is_report_a_suspected_breach_site(self.request.site):
            return reverse("report_a_suspected_breach:landing")
        elif is_view_a_suspected_breach_site(self.request.site):
            # if users are not accessing a specific page in view-a-suspected-breach - raise a 404
            # unless they are staff, in which case take them to the manage users page
            if self.request.user.is_staff:
                return reverse("view_a_suspected_breach:user_admin")
            else:
                raise Http404()
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
            response = redirect(self.request.session.pop("redirect_back_to", "/") + "?cookies_set=true")

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
