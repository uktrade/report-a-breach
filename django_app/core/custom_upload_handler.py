import uuid

from boto3 import client as boto3_client
from django.conf import settings
from django_chunk_upload_handlers.s3 import S3FileUploadHandler, ThreadedS3ChunkUploader


class CustomFileUploadHandler(S3FileUploadHandler):

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

    def new_file(self, *args: object, **kwargs: object) -> None:
        super().new_file(*args, **kwargs)
        self.new_file_name = self.file_name

        extra_kwargs = {}
        if endpoint_url := getattr(settings, "AWS_S3_ENDPOINT_URL", None):
            extra_kwargs["endpoint_url"] = endpoint_url

        extra_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        extra_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

        self.s3_client = boto3_client(
            "s3",
            region_name=settings.AWS_REGION,
            **extra_kwargs,
        )

        self.parts = []
        self.part_number = 1
        self.s3_key = f"chunk_upload_{str(uuid.uuid4())}"

        self.multipart = self.s3_client.create_multipart_upload(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=self.s3_key,
            ContentType=self.content_type,
        )

        self.upload_id = self.multipart["UploadId"]
        self.executor = ThreadedS3ChunkUploader(
            client=self.s3_client,
            bucket=settings.AWS_STORAGE_BUCKET_NAME,
            key=self.s3_key,
            upload_id=self.upload_id,
        )
