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


class CacheControlMiddleware:
    """Middleware that sets `Cache-Control` header to `no-cache`.

    We want the browser to always revalidate the content with the server before using a cached copy. We're not
    media-heavy, so the performance impact of this is minimal, and we'd rather have the most up-to-date content
    than a fast load time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers["Cache-Control"] = "no-cache"
        return response


class XSSProtectionMiddleware:
    """Middleware that sets `X-XSS-Protection` header to `0`.

    This may seem counter-intuitive, but it is recommended to disable the XSS protection header as it
    is not effective against modern XSS attacks and can introduce security vulnerabilities.

    https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html#x-xss-protection"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers["X-XSS-Protection"] = "0"
        return response
