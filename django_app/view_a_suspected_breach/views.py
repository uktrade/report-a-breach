from typing import Any

from core.sites import require_view_a_breach
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from .models import Users


@method_decorator(login_required, name="dispatch")
@method_decorator(require_view_a_breach(), name="dispatch")
class ViewABreachView(TemplateView):
    template_name = "view_a_suspected_breach/landing.html"


@method_decorator(login_required, name="dispatch")
@method_decorator(require_view_a_breach(), name="dispatch")
class AdminViewABreachView(TemplateView):
    template_name = "view_a_suspected_breach/user_admin.html"
    model = Users

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_data_object = self.get_model_data(**kwargs)
        user_data_pending = []
        user_data_accepted = []

        for user in user_data_object:
            id = user.id
            name = user.name
            email = user.email
            is_pending = user.is_pending
            if is_pending:
                user_data_pending.append((id, name, email, is_pending))
            else:
                user_data_accepted.append((id, name, email))

        context["pending_users"] = user_data_pending
        context["accepted_users"] = user_data_accepted

        return context

    def get_model_data(self, **kwargs: object) -> Any:
        return self.model.objects.all()

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        user_data = self.get_model_data(**kwargs)
        if update_user := self.request.GET.get("accept_user", None):
            user_data.get(id=update_user).update(is_pending=False)

        if delete_user := self.request.GET.get("delete_user", None):
            denied_user = user_data.get(id=delete_user)
            denied_user.delete()

        return super().get(request, **kwargs)
