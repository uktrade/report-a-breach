from collections import OrderedDict
from typing import Any, Iterable

import ring
from core.sites import (
    is_report_a_suspected_breach_site,
    is_view_a_suspected_breach_site,
)
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import RedirectView
from formtools.wizard.views import NamedUrlSessionWizardView


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


class RedirectBaseDomainView(RedirectView):
    """Redirects base url visits to either report a breach app or view app default view"""

    @property
    def url(self) -> str:
        if is_report_a_suspected_breach_site(self.request.site):
            return reverse("report_a_suspected_breach:landing")
        elif is_view_a_suspected_breach_site(self.request.site):
            return reverse("view_a_suspected_breach:landing")
        return ""
