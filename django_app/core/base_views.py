import datetime
from typing import Any

from django import forms
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, FormView, TemplateView
from playwright.sync_api import sync_playwright
from report_a_suspected_breach.utils import get_dirty_form_data


class BaseFormView(FormView):
    template_name = "core/base_form_step.html"

    # do we want to redirect the user to the redirect_to query parameter page after this form is submitted?
    redirect_after_post = True

    @property
    def step_name(self) -> str:
        """Get the step name from the view class name."""
        from report_a_suspected_breach.urls import view_to_step_dict

        step_name = view_to_step_dict[self.__class__.__name__]

        return step_name

    def post(self, request, *args, **kwargs):
        # checking for session expiry
        if last_activity := request.session.get(settings.SESSION_LAST_ACTIVITY_KEY, None):
            now = timezone.now()
            last_activity = datetime.datetime.fromisoformat(last_activity)
            # if the last recorded activity was more than the session cookie age ago, we assume the session has expired
            if now > (last_activity + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)):
                return redirect(reverse("session_expired"))
        else:
            # if we don't have a last activity, we assume the session has expired
            return redirect(reverse("session_expired"))

        # now setting the last active to the current time
        request.session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # we want to assign the form to the view ,so we can access it in the get_success_url method
        self.form = form

        # we want to store the dirty form data in the session, so we can access it later on
        form_data = dict(form.data.copy())

        # first get rid of some useless cruft
        form_data.pop("csrfmiddlewaretoken", None)
        form_data.pop("encoding", None)

        # Django QueryDict is a weird beast, we need to check if the key maps to a list of values (as it does with a
        # multi-select field) and if it does, we need to convert it to a list. If not, we can just keep the value as is.
        # We also need to keep the value as it is if the form is an ArrayField.
        for key, value in form_data.items():
            if not isinstance(form.fields.get(key), forms.MultipleChoiceField):
                if len(value) == 1:
                    form_data[key] = value[0]

        # check what (if any) fields have changed. This is useful if we want to control where the user gets redirected
        # to after the form is submitted depending on what they've changed
        self.changed_fields = {}
        if previous_data := get_dirty_form_data(self.request, self.step_name):
            for key, value in previous_data.items():
                if key in form_data and form_data[key] != value:
                    self.changed_fields[key] = value

        # now keep it in the session
        self.request.session[self.step_name] = form_data

        redirect_to_url = self.request.GET.get("redirect_to_url", None) or self.request.session.pop("redirect_to_url", None)
        if redirect_to_url and url_has_allowed_host_and_scheme(redirect_to_url, allowed_hosts=None):
            if self.redirect_after_post:
                # we want to redirect the user to a specific page after the form is submitted
                return redirect(redirect_to_url)
            else:
                # we don't want to redirect the user just now, but we want to pass the redirect_to URL to the next form,
                # so it can redirect the user after it is submitted
                self.request.session["redirect_to_url"] = redirect_to_url

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["request"] = self.request

        # restore the form data from the session, if it exists
        if self.request.method == "GET":
            if previous_data := get_dirty_form_data(self.request, self.step_name):
                kwargs["data"] = previous_data
        return kwargs


class BaseTemplateView(TemplateView):
    pass


class BaseDownloadPDFView(DetailView):
    template_name = "core/base_download_pdf.html"
    header = "Report a suspected breach"

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        self.reference = self.request.GET.get("reference", "")
        filename = f"report-{self.reference}.pdf"
        pdf_data = None
        template_string = render_to_string(self.template_name, context=self.get_context_data(**kwargs))
        margins = {"left": "3.17in", "right": "3.17in"}

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(mark_safe(template_string))
            page.wait_for_function("document.fonts.ready.then(fonts => fonts.status === 'loaded')")
            pdf_data = page.pdf(format="A4", tagged=True, margin=margins)
            response = HttpResponse(pdf_data, content_type="application/pdf")
            browser.close()

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={filename}"
        return response

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        self.object = []
        context = super().get_context_data(**kwargs)
        context["header"] = self.header
        context["reference"] = self.reference
        return context
