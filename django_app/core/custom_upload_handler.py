from typing import Any

from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler
from django_chunk_upload_handlers.clam_av import (
    FileWithVirus,
    VirusFoundInFileException,
)


class CustomFileUploadHandler(FileUploadHandler):
    def receive_data_chunk(self, raw_data: Any, start: Any) -> Any:
        return raw_data

    def file_complete(self, file_size: float | None) -> FileWithVirus | None:
        """
        Check if scanned file has a virus or not.
        If it does, raise an exception on the form.
        """
        if "clam_av_results" in self.content_type_extra:
            for result in self.content_type_extra["clam_av_results"]:
                if result["file_name"] == self.file_name:
                    # Set AV headers
                    if not result["av_passed"]:
                        if settings.CHUNK_UPLOADER_RAISE_EXCEPTION_ON_VIRUS_FOUND:
                            raise VirusFoundInFileException()
                        else:
                            return FileWithVirus(field_name=self.field_name)
        return None
