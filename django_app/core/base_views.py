from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView
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
        for key, value in form_data.items():
            if len(value) == 1:
                form_data[key] = value[0]

        # now keep it in the session
        self.request.session[self.step_name] = form_data

        redirect_to_url = self.request.GET.get("redirect_to_url", None) or self.request.session.pop("redirect_to_url", None)
        if redirect_to_url:
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