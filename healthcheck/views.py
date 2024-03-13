import time

from django.shortcuts import render
from django.views.generic import View


class HealthCheckView(View):
    """Checks the status of the Report a Breach service itself, and all other backing services.

    Returns an XML file containing the response time and the results of these checks, used by Pingdom to monitor
    the health of the service."""

    def get(self, request, *args, **kwargs):
        from healthcheck.checks import db_check, s3_check

        start = time.time()
        db_check = db_check()
        s3_check = s3_check()
        all_good = db_check and s3_check

        end = time.time()
        time_taken = round(end - start, 3)

        return render(
            request,
            "healthcheck.html",
            context={"all_good": all_good, "time_taken": time_taken},
            content_type="text/xml",
        )
