from core.sites import (
    is_report_a_suspected_breach_site,
    is_view_a_suspected_breach_site,
)
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, RedirectView
from formtools.wizard.views import NamedUrlSessionWizardView


class BaseView(FormView):
    # TODO: decide if we need to recreate form.html or other template to use here
    # template_name = "form.html"
    pass


class BaseModelFormView(BaseView):
    def __init__(self):
        super().__init__()

    def form_valid(self, form):
        breach_instance = form.save(commit=False)
        session_data = self.request.session.get("breach_instance", {})
        if "id" not in session_data.keys():
            session_data["id"] = str(breach_instance.id)
        form_data = form.cleaned_data
        session_data.update({key: value for key, value in form_data.items()})
        self.request.session["breach_instance"] = session_data
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(self.success_path, kwargs={"pk": self.request.session["breach_instance"]["id"]})


class BaseWizardView(NamedUrlSessionWizardView):
    template_names_lookup = {}

    def get_template_names(self):
        if custom_template_name := self.template_names_lookup.get(self.steps.current, None):
            return custom_template_name
        return super().get_template_names()

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if custom_getter := getattr(self, f"get_{self.steps.current}_context_data", None):
            context = custom_getter(form, context)
        if form_h1_header := getattr(form, "form_h1_header", None):
            context["form_h1_header"] = form_h1_header
        return context

    def process_step(self, form):
        if custom_getter := getattr(self, f"process_{self.steps.current}_step", None):
            return custom_getter(form)
        return super().process_step(form)

    def render(self, form=None, **kwargs):

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
            if form.is_valid():
                self.request.session["redirect"] = None
                return self.render_goto_step(redirect_to)
        return super().render(form, **kwargs)

    def post(self, *args, **kwargs):
        # allow the user to change previously entered data and be redirected
        # back to the summary page once complete
        if redirect_to := self.request.GET.get("redirect", None):
            self.request.session["redirect"] = redirect_to
            self.request.session.modified = True

        if self.steps.current == "where_were_the_goods_made_available_to":
            self.request.session["made_available_journey"] = True
            self.request.session.modified = True

        return super().post(*args, **kwargs)

    def get_all_cleaned_data(self):
        """
        Overriding this as want the cleaned_data dictionary to have a key per form, not 1 big dictionary with all the
        form's cleaned_data
        """
        cleaned_data = {}
        for form_key in self.get_form_list():
            form_obj = self.get_form(
                step=form_key, data=self.storage.get_step_data(form_key), files=self.storage.get_step_files(form_key)
            )
            if form_obj.is_valid():
                cleaned_data[form_key] = form_obj.cleaned_data
        return cleaned_data

    def get_cleaned_data_for_step(self, step):
        """overriding this to return an empty dictionary if the form is not valid or the step isn't found.

        This makes it easier to write self.get_cleaned_data_for_step.get("value")"""
        if step in self.form_list:
            form_obj = self.get_form(
                step=step,
                data=self.storage.get_step_data(step),
                files=self.storage.get_step_files(step),
            )
            if form_obj.is_valid() and form_obj.cleaned_data:
                return form_obj.cleaned_data
        return {}


class RedirectBaseDomainView(RedirectView):
    """Redirects base url visits to either report a breach app or view app default view"""

    def get_redirect_url(self, *args, **kwargs):
        if is_report_a_suspected_breach_site(self.request.site):
            self.url = reverse("report_a_suspected_breach:landing")
        elif is_view_a_suspected_breach_site(self.request.site):
            self.url = reverse("view_a_suspected_breach:landing")
        return super().get_redirect_url(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        url = self.get_redirect_url(*args, **kwargs)
        host = request.get_host()
        raw_host = request._get_raw_host()
        site_domains = [each.domain for each in Site.objects.all()]
        site_name = [each.name for each in Site.objects.all()]
        print(host)
        print(site_domains)
        print(site_name)
        print(raw_host)

        if url:
            return HttpResponseRedirect(url)
        else:
            raise Exception()
