from core.sites import require_view_a_breach
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


@method_decorator(require_view_a_breach(), name="dispatch")
class ViewABreachView(TemplateView):
    template_name = "view_a_suspected_breach/landing.html"
