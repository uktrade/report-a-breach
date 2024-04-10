import functools

from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied


class SiteName:
    view_a_suspected_breach = "view-a-suspected-breach"
    report_a_suspected_breach = "report-a-suspected-breach"


def require_view_a_breach():
    def decorator(f):
        """Decorator to require that a view only accepts requests from the view a breach site."""

        @functools.wraps(f)
        def _wrapped_view(request, *args, **kwargs):
            if not is_view_a_suspected_breach_site(request.site):
                raise PermissionDenied("View a breach feature requires view a breach site.")

            return f(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def require_report_a_suspected_breach():
    def decorator(func):
        """Decorator to require that a view only accepts requests from the report a breach site."""

        @functools.wraps(func)
        def _wrapped_view(request, *args, **kwargs):
            if not is_report_a_suspected_breach_site(request.site):
                raise PermissionDenied("Report a breach feature requires report a breach site.")
            return func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def is_report_a_suspected_breach_site(site: Site) -> bool:
    return site.name == SiteName.report_a_suspected_breach


def is_view_a_suspected_breach_site(site: Site) -> bool:
    return site.name == SiteName.view_a_suspected_breach
