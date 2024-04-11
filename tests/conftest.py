import pytest
from core.sites import SiteName
from django.contrib.sites.models import Site

from tests.helpers import get_test_client


@pytest.fixture()
def rasb_client(db):
    """Client used to access the report-a-suspected-breach site.

    No user is logged in with this client.
    """
    rab_site = Site.objects.get(name=SiteName.report_a_suspected_breach)
    return get_test_client(rab_site.domain)


@pytest.fixture()
def vasb_client(db):
    """Client used to access the view-a-suspected-breach site.

    No user is logged in with this client.
    """
    vab_site = Site.objects.get(name=SiteName.view_a_suspected_breach)
    return get_test_client(vab_site.domain)
