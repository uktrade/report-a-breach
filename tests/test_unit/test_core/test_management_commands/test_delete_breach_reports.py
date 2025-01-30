from django.core.management import call_command
from report_a_suspected_breach.models import Breach

from tests.factories import BreachFactory


def test_successful_delete(db):
    BreachFactory(reference="123")
    BreachFactory(reference="456")

    assert Breach.objects.count() == 2

    call_command("delete_breach_reports", ["123", "456"])
    assert Breach.objects.count() == 0


def test_doesnt_exist_delete(db):
    BreachFactory(reference="123")

    assert Breach.objects.count() == 1

    call_command("delete_breach_reports", ["456"])
    assert Breach.objects.count() == 1
