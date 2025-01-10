from django.test import override_settings

from tests.helpers import reload_urlconf


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
