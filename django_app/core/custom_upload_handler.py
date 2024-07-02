from django_chunk_upload_handlers.s3 import S3FileUploadHandler
from storages.backends.s3 import S3File


class CustomFileUploadHandler(S3FileUploadHandler):
    def file_complete(self, file_size: int) -> S3File:
        """We override this method so we can define a new file name which is the session key + the original file name"""
        self.new_file_name = f"{self.request.session.session_key}/{self.file_name}"
        return super().file_complete(file_size)
