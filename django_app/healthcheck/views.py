import time

from config.env import DBTPlatformSettings, env
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import View
from healthcheck.checks import db_check, s3_check


class HealthCheckView(View):
    """Checks the status of the Report a Breach service itself, and all other backing services.

    Returns an XML file containing the response time and the results of these checks, used by Pingdom to monitor
    the health of the service."""

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        # we want to disable the healthcheck if we're building on DBT Platform
        if isinstance(env, DBTPlatformSettings) and env.in_build_step:
            return HttpResponse(status=200)

        start = time.time()
        is_db_good = db_check()
        is_s3_good = s3_check()
        all_good = is_db_good and is_s3_good

        end = time.time()
        time_taken = round(end - start, 3)

        return render(
            request,
            "healthcheck.html",
            context={"all_good": all_good, "time_taken": time_taken},
            content_type="text/xml",
        )
