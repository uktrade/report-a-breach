from typing import Any

from core.sites import require_view_a_breach
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from utils.notifier import send_email


@method_decorator(login_required, name="dispatch")
@method_decorator(require_view_a_breach(), name="dispatch")
class ViewABreachView(TemplateView):
    template_name = "view_a_suspected_breach/landing.html"

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        user_objects = User.objects.all()
        user_data = user_objects.get(pk=request.user.id)
        admin_url = reverse("view_a_suspected_breach:user_admin")

        if user_data.is_active:
            for user in user_objects:
                if user.is_staff:
                    send_email(
                        email=user.email,
                        template_id=settings.EMAIL_VASB_USER_ADMIN_TEMPLATE_ID,
                        context={"admin_url": admin_url},
                    )
            return render(request, "view_a_suspected_breach/unauthorised.html")

        return super().get(request, **kwargs)


@method_decorator(login_required, name="dispatch")
@method_decorator(require_view_a_breach(), name="dispatch")
class AdminViewABreachView(TemplateView):
    template_name = "view_a_suspected_breach/user_admin.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user_data_objects = self.get_user_data(**kwargs)
        user_data_pending = []
        user_data_accepted = []

        for user in user_data_objects:
            id = user.id
            first_name = user.first_name
            last_name = user.last_name
            email = user.email
            is_active = user.is_active
            if not is_active:
                user_data_accepted.append((id, f"{first_name} {last_name}", email))
            else:
                user_data_pending.append((id, f"{first_name} {last_name}", email, is_active))

        context["pending_users"] = user_data_pending
        context["accepted_users"] = user_data_accepted

        return context

    @staticmethod
    def get_user_data(**kwargs: object) -> User:
        return User.objects.all()

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        user_data = self.get_user_data(**kwargs)

        if update_user := self.request.GET.get("accept_user", None):
            user_to_accept = user_data.get(id=update_user)
            user_to_accept.is_active = False
            user_to_accept.save()
            self.get_context_data(**kwargs)

        if delete_user := self.request.GET.get("delete_user", None):
            denied_user = user_data.get(id=delete_user)
            denied_user.delete()
            self.get_context_data(**kwargs)

        return super().get(request, **kwargs)
