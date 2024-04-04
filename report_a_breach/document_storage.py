from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class TemporaryDocumentStorage(S3Boto3Storage):
    bucket_name = settings.TEMPORARY_S3_BUCKET_NAME


class PermanentDocumentStorage(S3Boto3Storage):
    bucket_name = settings.PERMANENT_S3_BUCKET_NAME
