import os

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import FileUploadHandler
from django_chunk_upload_handlers.clam_av import (
    FileWithVirus,
    VirusFoundInFileException,
)

CHUNK_UPLOADER_RAISE_EXCEPTION_ON_VIRUS_FOUND = getattr(
    settings,
    "CHUNK_UPLOADER_RAISE_EXCEPTION_ON_VIRUS_FOUND",
    False,
)


class CustomFileUploadHandler(FileUploadHandler):

    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super().new_file(*args, **kwargs)
        self.file = TemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)

    def receive_data_chunk(self, raw_data, start):
        self.file.write(raw_data)

    def file_complete(self, file_size):
        """
        Check if scanned file has a virus or not.
        If it does, raise an exception on the form.
        """
        if "clam_av_results" in self.content_type_extra:
            for result in self.content_type_extra["clam_av_results"]:
                if result["file_name"] == self.file_name:
                    # Set AV headers
                    if result["av_passed"]:
                        self.file.seek(0)
                        self.file.size = file_size
                    else:
                        if hasattr(self, "file"):
                            temp_location = self.file.temporary_file_path()
                            try:
                                self.file.close()
                                os.remove(temp_location)
                            except FileNotFoundError:
                                pass

                        if CHUNK_UPLOADER_RAISE_EXCEPTION_ON_VIRUS_FOUND:
                            raise VirusFoundInFileException()
                        else:
                            return FileWithVirus(field_name=self.field_name)

        return self.file

    def upload_interrupted(self):
        if hasattr(self, "file"):
            temp_location = self.file.temporary_file_path()
            try:
                self.file.close()
                os.remove(temp_location)
            except FileNotFoundError:
                pass
