from django.urls import reverse
from django.views.generic import FormView
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
        return context

    def process_step(self, form):
        if custom_getter := getattr(self, f"process_{self.steps.current}_step", None):
            return custom_getter(form)
        return super().process_step(form)

    def render(self, form=None, **kwargs):
        if self.steps.current == "verify":
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

        return super().post(*args, **kwargs)

    def get_all_cleaned_data(self):
        """
        Returns a merged dictionary of all step cleaned_data dictionaries.
        If a step contains a `FormSet`, the key will be prefixed with
        'formset-' and contain a list of the formset cleaned_data dictionaries.
        """
        cleaned_data = {}
        for form_key in self.get_form_list():
            form_obj = self.get_form(
                step=form_key, data=self.storage.get_step_data(form_key), files=self.storage.get_step_files(form_key)
            )
            if form_obj.is_valid():
                cleaned_data[form_key] = form_obj.cleaned_data
        return cleaned_data
