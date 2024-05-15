from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, reverse
from utils.notifier import send_email


class ActiveUserRequiredMixin:
    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if not request.user.is_active:
            for user in User.objects.filter(is_staff=True):
                if user.is_staff:
                    send_email(
                        email=user.email,
                        template_id=settings.EMAIL_VASB_USER_ADMIN_TEMPLATE_ID,
                        context={"admin_url": reverse("view_a_suspected_breach:user_admin")},
                    )
            return render(request, "view_a_suspected_breach/unauthorised.html")

        return super().dispatch(request, **kwargs)


class StaffUserOnlyMixin:
    def dispatch(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        if not request.user.is_staff:
            return HttpResponse("Not authorized", status=401)
        return super().dispatch(request, **kwargs)
