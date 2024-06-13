from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, reverse
from utils.notifier import send_email


class ActiveUserRequiredMixin:
    def dispatch(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        if not request.user.is_active:
            admin_url = reverse("view_a_suspected_breach:user_admin")
            user_login_datetime = f"{datetime.now():%Y-%m-%d %H:%M:%S%z}"
            for user in User.objects.filter(is_staff=True):
                send_email(
                    email=user.email,
                    template_id=settings.EMAIL_VASB_USER_ADMIN_TEMPLATE_ID,
                    context={
                        "user_email": request.user.email,
                        "user_login_datetime": user_login_datetime,
                        "admin_url": f"{settings.VIEW_A_SUSPECTED_BREACH_DOMAIN}{admin_url}#pending",
                    },
                )
            return render(request, "view_a_suspected_breach/unauthorised.html")

        return super().dispatch(request, **kwargs)


class StaffUserOnlyMixin(ActiveUserRequiredMixin):
    def dispatch(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        if not request.user.is_staff:
            return HttpResponse("Not authorized", status=401)
        return super().dispatch(request, **kwargs)
