from django.urls import reverse
from django.views.generic import FormView
from formtools.wizard.views import NamedUrlSessionWizardView


class BaseView(FormView):
    template_name = "form.html"


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
        return reverse(
            self.success_path, kwargs={"pk": self.request.session["breach_instance"]["id"]}
        )


class BaseWizardView(NamedUrlSessionWizardView):
    def get_template_names(self):
        if custom_getter := getattr(self, f"get_{self.steps.current}_template_name", None):
            return custom_getter()
        return super().get_template_names()

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if custom_getter := getattr(self, f"get_{self.steps.current}_context_data", None):
            context.update(custom_getter(form))
        return context

    def process_step(self, form):
        if custom_getter := getattr(self, f"process_{self.steps.current}_step", None):
            return custom_getter(form)
        return super().process_step(form)

    def process_edited_form_field(self, form):
        # this ensures the changed data from a form resubmission is saved to the cleaned dictionary
        if form.is_valid():
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            self.storage.set_step_files(self.steps.current, self.process_step_files(form))

    def post(self, *args, **kwargs):
        full_path = self.request.get_full_path()
        session = self.request.session
        summary_step = "summary"
        form = self.get_form(data=self.request.POST, files=self.request.FILES)

        # allows a user to change a form then return to the summary page
        # after successful resubmission
        if "redirect=true" in full_path:
            if "email" in full_path:
                session["redirect"] = True
                self.get_cleaned_data_for_step(self.steps.current)
                return super().post(*args, **kwargs)
            self.process_edited_form_field(form)
            return self.render_goto_step(summary_step, **kwargs)

        # we need to check if the user redirected to the email page and if so, send them back to
        # summary after the verify page
        elif "verify" in full_path:
            return (
                self.render_goto_step(summary_step, **kwargs)
                if session.get("redirect")
                else super().post(*args, **kwargs)
            )

        return super().post(*args, **kwargs)
