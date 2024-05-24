import sys
from importlib import import_module, reload

from django.conf import settings
from django.test import override_settings


def reload_urlconf():
    if settings.ROOT_URLCONF in sys.modules:
        reload(sys.modules[settings.ROOT_URLCONF])
    return import_module(settings.ROOT_URLCONF)


@override_settings(ROOT_URLCONF="core.debug_urls")
def test_admin_accessible_on_local(vasb_client):
    reload_urlconf()
    response = vasb_client.get("/admin", follow=True)
    assert response.status_code == 200


@override_settings(ROOT_URLCONF="core.urls")
def test_admin_not_accessible_on_deploy(vasb_client):
    reload_urlconf()
    response = vasb_client.get("/admin")
    assert response.status_code == 404
