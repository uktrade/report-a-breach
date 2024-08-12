import pytest
from core.sites import SiteName
from django.contrib.sites.models import Site
from django.test import Client, RequestFactory

from tests.factories import (
    BreachBreacherAndSupplierFactory,
    BreachFactory,
    BreachWith2SanctionsFactory,
    BreachWithCompaniesHouseFactory,
)
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


@pytest.fixture()
def breach_object(db):
    """Fixture to create a breach object."""
    return BreachFactory()


@pytest.fixture()
def request_object(rasb_client: Client, method: str = "GET"):
    """Fixture to create a request object."""
    request_object = RequestFactory()
    request_object.session = rasb_client.session
    request_object.method = method
    request_object.GET = {}
    request_object.POST = {}
    return request_object


@pytest.fixture()
def breach_with_sanctions_object(db):
    """Fixture to create a breach with sanctions object"""
    return BreachWith2SanctionsFactory()


@pytest.fixture()
def breach_with_companies_house_object(db):
    """Fixture to create a breach with companies house object"""
    return BreachWithCompaniesHouseFactory()


@pytest.fixture()
def breacher_and_supplier_object(db):
    """Fixture to create a breach object where the breacher is the supplier"""
    return BreachBreacherAndSupplierFactory()
