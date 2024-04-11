from . import is_report_a_suspected_breach_site, is_view_a_suspected_breach_site


def sites(request):
    return {
        "is_report_a_suspected_breach_site": is_report_a_suspected_breach_site(request.site),
        "is_view_a_suspected_breach_site": is_view_a_suspected_breach_site(request.site),
    }
