import functools

from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied


class SiteName:
    VIEW_A_BREACH = "view-a-breach"
    REPORT_A_BREACH = "report-a-breach"


def require_view_a_breach():
    def decorator(f):
        """Decorator to require that a view only accepts requests from the view a breach site."""

        @functools.wraps(f)
        def _wrapped_view(request, *args, **kwargs):
            if not is_view_a_breach_site(request.site):
                raise PermissionDenied("View a breach feature requires view a breach site.")

            return f(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def require_report_a_breach():
    def decorator(func):
        """Decorator to require that a view only accepts requests from the report a breach site."""

        @functools.wraps(func)
        def _wrapped_view(request, *args, **kwargs):
            if not is_report_a_breach_site(request.site):
                raise PermissionDenied("Report a breach feature requires report a breach site.")
            return func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def is_report_a_breach_site(site: Site) -> bool:
    return site.name == SiteName.REPORT_A_BREACH


def is_view_a_breach_site(site: Site) -> bool:
    return site.name == SiteName.VIEW_A_BREACH
