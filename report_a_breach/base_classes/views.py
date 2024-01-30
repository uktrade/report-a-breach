from django.urls import reverse
from django.views.generic import FormView


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
