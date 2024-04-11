from django.http import HttpResponse
from django.test import Client


def get_test_client(server_name: str) -> Client:
    """Create a test client for a particular site.

    :param server_name: Domain to link to the correct site.

    """
    client = Client(SERVER_NAME=server_name)

    return client


def get_response_content(response: HttpResponse) -> str:
    """Get the body of a response as a string.

    :param response: The response to get the body of.

    """
    return response.content.decode("utf-8")
