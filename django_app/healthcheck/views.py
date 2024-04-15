import time

from django.shortcuts import render
from django.views.generic import View
from healthcheck.checks import db_check, s3_check


class HealthCheckView(View):
    """Checks the status of the Report a Breach service itself, and all other backing services.

    Returns an XML file containing the response time and the results of these checks, used by Pingdom to monitor
    the health of the service."""

    def get(self, request, *args, **kwargs):
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
