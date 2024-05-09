import magic
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest


def get_mime_type(file: UploadedFile) -> str:
    """
    Get MIME by reading the header of the file
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)
    return mime_type


def is_ajax(request: HttpRequest) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"
