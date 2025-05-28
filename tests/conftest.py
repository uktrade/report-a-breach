from unittest import mock

import notifications_python_client
import pytest
from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage
from core.sites import SiteName
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import Client, RequestFactory
from django.utils import timezone
from utils import notifier

from tests.factories import (
    BreachBreacherAndSupplierFactory,
    BreachFactory,
    BreachWith2SanctionsFactory,
    BreachWithCompaniesHouseFactory,
    UploadedDocumentFactory,
    WhistleblowerReportFactory,
)
from tests.helpers import get_test_client


@pytest.fixture()
def rasb_client(db):
    """Client used to access the report-a-suspected-breach site.

    No user is logged in with this client.
    """
    rab_site = Site.objects.get(name=SiteName.report_a_suspected_breach)

    rasb_client = get_test_client(rab_site.domain, "report-a-suspected-breach")
    session = rasb_client.session
    session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()
    session.save()
    return rasb_client


@pytest.fixture()
def vasb_client(db):
    """Client used to access the view-a-suspected-breach site.

    No user is logged in with this client.
    """
    vab_site = Site.objects.get(name=SiteName.view_a_suspected_breach)
    return get_test_client(vab_site.domain, http_host="view-a-suspected-breach")


@pytest.fixture()
def staff_user(db):
    return User.objects.create_user(
        "staff",
        "staff@example.com",
        is_active=True,
        is_staff=True,
    )


@pytest.fixture()
def vasb_client_logged_in(vasb_client, staff_user) -> Client:
    """Client used to access the view-a-licence site.

    A user is logged in with this client"""

    vasb_client.force_login(staff_user)
    return vasb_client


@pytest.fixture()
def breach_object(db):
    """Fixture to create a breach object."""
    return BreachFactory()


@pytest.fixture()
def whistleblower_report_object(db):
    """Fixture to create a breach object."""
    return WhistleblowerReportFactory()


@pytest.fixture()
def request_object(rasb_client: Client, method: str = "GET"):
    """Fixture to create a request object."""
    request_object = RequestFactory()
    request_object.session = rasb_client.session
    request_object.method = method
    request_object.GET = {}
    request_object.POST = {}
    request_object.scheme = "http"
    request_object.META = {"HTTP_HOST": "report-a-suspected-breach"}
    request_object.path = "tasklist"
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


@pytest.fixture(autouse=True)
def patched_send_email(monkeypatch):
    """We don't want to send emails when running tests"""
    mock_notifications_api_client = mock.create_autospec(notifications_python_client.notifications.NotificationsAPIClient)
    monkeypatch.setattr(notifier, "NotificationsAPIClient", mock_notifications_api_client)


@pytest.fixture()
def uploaded_document_object(db):
    return UploadedDocumentFactory()


@pytest.fixture()
def delete_all_permanent_bucket_files():
    """Fixture to delete all files in the permanent bucket. Both before and after tests"""
    for obj in PermanentDocumentStorage().bucket.objects.all():
        obj.delete()

    yield

    for obj in PermanentDocumentStorage().bucket.objects.all():
        obj.delete()


@pytest.fixture()
def delete_all_temporary_bucket_files():
    """Fixture to delete all files in the temporary bucket. Both before and after tests"""
    for obj in TemporaryDocumentStorage().bucket.objects.all():
        obj.delete()

    yield

    for obj in TemporaryDocumentStorage().bucket.objects.all():
        obj.delete()
