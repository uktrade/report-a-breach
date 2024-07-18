from django.views.generic import FormView
from report_a_suspected_breach.utils import get_dirty_form_data


class BaseFormView(FormView):
    template_name = "core/base_form_step.html"

    @property
    def step_name(self) -> str:
        """Get the step name from the view class name."""
        from report_a_suspected_breach.urls import view_to_step_dict

        step_name = view_to_step_dict[self.__class__.__name__]
        return step_name

    def form_valid(self, form):
        # we want to assign the form to the view ,so we can access it in the get_success_url method
        self.form = form

        # we want to store the dirty form data in the session, so we can access it later on
        self.request.session[self.step_name] = form.data

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["request"] = self.request

        # restore the form data from the session, if it exists
        if self.request.method == "GET":
            kwargs["data"] = get_dirty_form_data(self.request, self.step_name)
        return kwargs
