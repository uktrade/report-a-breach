from django.contrib.sites.middleware import CurrentSiteMiddleware
from django.http import HttpRequest
from django.urls import resolve


class ReportASuspectedBreachCurrentSiteMiddleware(CurrentSiteMiddleware):
    """Middleware that sets `site` attribute to request object."""

    # List of views that do not add the site to the current request object.
    site_exempt_views = [
        "healthcheck:healthcheck_ping",
    ]

    def process_request(self, request: HttpRequest) -> None:
        """Middleware that sets `site` attribute to request object."""
        if resolve(request.path).view_name not in self.site_exempt_views:
            super().process_request(request)


class SetPermittedCrossDomainPolicyHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        return response
