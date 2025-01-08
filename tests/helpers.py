import sys
from importlib import import_module, reload

from django.conf import settings
from django.http import HttpResponse
from django.test import Client
from django.urls import clear_url_caches


def get_test_client(server_name: str, http_host: str) -> Client:
    """Create a test client for a particular site.

    :param server_name: Domain to link to the correct site.

    """
    client = Client(SERVER_NAME=server_name, HTTP_HOST=http_host)

    return client


def get_response_content(response: HttpResponse) -> str:
    """Get the body of a response as a string.

    :param response: The response to get the body of.

    """
    return response.content.decode("utf-8")


def reload_urlconf():
    clear_url_caches()
    if settings.ROOT_URLCONF in sys.modules:
        reload(sys.modules[settings.ROOT_URLCONF])
    return import_module(settings.ROOT_URLCONF)
