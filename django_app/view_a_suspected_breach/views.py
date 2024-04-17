from core.sites import require_view_a_breach
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import FileFieldForm


@method_decorator(login_required, name="dispatch")
@method_decorator(require_view_a_breach(), name="dispatch")
class ViewABreachView(TemplateView):
    template_name = "view_a_suspected_breach/landing.html"


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "view_a_suspected_breach/upload_documents.html"  # Replace with your template.
    success_url = "..."  # Replace with your URL or reverse().

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        for f in files:
            print(f)
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
