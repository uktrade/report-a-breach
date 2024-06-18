from django.shortcuts import redirect
from report_a_suspected_breach.models import ReporterEmailVerification


class EmailVerifiedRequiredMixin:
    """Ensures that the user has verified their email address before accessing the view."""

    def dispatch(self, request, *args, **kwargs):
        verification_object = ReporterEmailVerification.objects.filter(
            reporter_session=request.session.session_key,
            verified=True,
        )
        if not verification_object:
            # they haven't verified their email address, redirect them to the email verification page
            return redirect("report_a_suspected_breach:email_verify")

        return super().dispatch(request, *args, **kwargs)
