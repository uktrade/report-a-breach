from collections import OrderedDict
from typing import Any, Iterable

import ring
from core.sites import (
    is_report_a_suspected_breach_site,
    is_view_a_suspected_breach_site,
)
from django.forms import Form
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView
from django_ratelimit.exceptions import Ratelimited
from formtools.wizard.views import NamedUrlSessionWizardView
from report_a_suspected_breach.tasklist import get_tasklist

from .forms import CookiesConsentForm, HideCookiesForm


class BaseWizardView(NamedUrlSessionWizardView):
    template_names_lookup = {}

    def __str__(self) -> str:
        return "report_a_suspected_breach_wizard_view"

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        response = super().dispatch(request, *args, **kwargs)
        response.tasklist = getattr(self, "tasklist", None)
        return response

    def get_template_names(self) -> list[str]:
        if custom_template_name := self.template_names_lookup.get(self.steps.current, None):
            return custom_template_name
        return super().get_template_names()

    def get_context_data(self, form: Form, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(form=form, **kwargs)
        if custom_getter := getattr(self, f"get_{self.steps.current}_context_data", None):
            context = custom_getter(form, context)
        if form_h1_header := getattr(form, "form_h1_header", None):
            context["form_h1_header"] = form_h1_header
        return context

    def process_step(self, form: Form) -> dict[str, Any]:
        """Overriding this method to allow for custom processing of each step in the wizard."""

        # the user has just POSTED, we need to clear the lru_cache for the corresponding step in the
        # get_cleaned_data_for_step method as the data may be overwritten
        self.get_cleaned_data_for_step.delete(self.steps.current)

        # if a custom processor exists for the current step, call it
        if custom_getter := getattr(self, f"process_{self.steps.current}_step", None):
            return custom_getter(form)
        return super().process_step(form)

    def render(self, form: Form | None = None, **kwargs: object) -> HttpResponse:
        """Controls the rendering of the response."""
        if self.steps.current == "do_you_know_the_registered_company_number" and self.request.session.get("company_details_500"):
            return HttpResponseRedirect(
                reverse("report_a_suspected_breach:step", kwargs={"step": "manual_companies_house_input"}) + "?start=true"
            )

        steps_to_continue = [
            "verify",
            "business_or_person_details",
            "check_company_details",
            "about_the_supplier",
            "about_the_end_user",
        ]

        if self.steps.current in steps_to_continue:
            return super().render(form, **kwargs)

        # if we have a redirect set in the session, we want to redirect to that step, but only if the form is valid.
        # if the form is not valid, we want to show the user the errors on the current step
        elif redirect_to := self.request.session.get("redirect"):
            if form is not None:
                if form.is_valid():
                    self.request.session["redirect"] = None
                    # redirect to summary rather than tasklist summary
                    if redirect_to == "summary":
                        return HttpResponseRedirect(
                            reverse("report_a_suspected_breach:step", kwargs={"step": "summary"}) + "?start=true"
                        )
                    else:
                        return self.render_goto_step(redirect_to)
        return super().render(form, **kwargs)

    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        # allow the user to change previously entered data and be redirected
        # back to the summary page once complete
        if redirect_to := self.request.GET.get("redirect", None):
            self.request.session["redirect"] = redirect_to
            self.request.session.modified = True

        if self.steps.current == "where_were_the_goods_made_available_to":
            self.request.session["made_available_journey"] = True
            self.request.session.modified = True

        return super().post(*args, **kwargs)

    def get_all_cleaned_data(self) -> dict[str, Any]:
        """
        Overriding this as want the cleaned_data dictionary to have a key per form, not 1 big dictionary with all the
        form's cleaned_data
        """
        cleaned_data = {}
        for form_key in self.get_form_list():
            if form_key == "about_the_end_user" or form_key == "end_user_added":
                continue
            form_obj = self.get_form(
                step=form_key, data=self.storage.get_step_data(form_key), files=self.storage.get_step_files(form_key)
            )
            if form_obj.is_valid():
                cleaned_data[form_key] = form_obj.cleaned_data
        return cleaned_data

    @ring.lru()
    def get_cleaned_data_for_step(self, step: str) -> dict[Any, Any]:
        """overriding this to return an empty dictionary if the form is not valid or the step isn't found.

        This makes it easier to write self.get_cleaned_data_for_step.get({value})

        We also add an LRU cache to this method as it is constantly called as part of the form validation process, and
        also for checking where the user is in the overall tasklist. So we cache the results of this and invalidate
        the cache for a particular step is the user has just POSTed data to that step.
        """
        if step in self.form_list:
            form_obj = self.get_form(
                step=step,
                data=self.storage.get_step_data(step),
                files=self.storage.get_step_files(step),
            )
            if form_obj.is_valid() and form_obj.cleaned_data:
                return form_obj.cleaned_data
        return {}

    def get_form(self, step: str | None = None, data: Any = None, files: Iterable | None = None, **kwargs: object) -> Form:
        """Overriding this method, so it calls self.form_list rather than self.get_form_list().

        The latter will apply the conditional logic to the form list, which we don't want to do here.
        """
        if step is None:
            step = self.steps.current
        form_class = self.form_list[step]
        kwargs = self.get_form_kwargs(step)
        kwargs.update(
            {
                "data": data,
                "files": files,
                "prefix": self.get_form_prefix(step, form_class),
                "initial": self.get_form_initial(step),
            }
        )
        return form_class(**kwargs)

    def render_done(self, form: Form, **kwargs: object) -> HttpResponse:
        """
        Overwriting this method as there are some forms we don't want to revalidate on done, so we need to check if the
        form has a revalidate_on_done attribute set to False. If it does, we don't want to revalidate the form when
        the user is done.
        """
        final_forms = OrderedDict()
        # walk through the form list and try to validate the data again.
        for form_key in self.get_form_list():
            form_obj = self.get_form(
                step=form_key, data=self.storage.get_step_data(form_key), files=self.storage.get_step_files(form_key)
            )
            if not form_obj.is_valid() and form_obj.revalidate_on_done:
                return self.render_revalidation_failure(form_key, form_obj, **kwargs)
            final_forms[form_key] = form_obj

        # render the done view and reset the wizard before returning the
        # response. This is needed to prevent from rendering done with the
        # same data twice.
        done_response = self.done(list(final_forms.values()), form_dict=final_forms, **kwargs)
        self.storage.reset()
        return done_response


class BaseTemplateView(TemplateView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasklist = get_tasklist(self, non_wizard_view=True)

    def get_steps(self) -> list[str]:
        step_list = []
        for task in self.tasklist.tasks:
            step_list.extend(task.form_steps.keys())
        return step_list

    def get_step_url(self, step: str) -> str:
        # TODO: tidy for loops
        steps = self.get_steps()
        for step_name in steps:
            if step_name == step:
                for task in self.tasklist.tasks:
                    if step_name in task.form_steps:
                        return task.start_url
        return reverse_lazy("report_a_suspected_breach:landing")


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
