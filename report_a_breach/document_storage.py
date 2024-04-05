from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class TemporaryDocumentStorage(S3Boto3Storage):
    bucket_name = settings.TEMPORARY_S3_BUCKET_NAME
    access_key = settings.TEMPORARY_S3_BUCKET_ACCESS_KEY_ID
    secret_key = settings.TEMPORARY_S3_BUCKET_SECRET_ACCESS_KEY


class PermanentDocumentStorage(S3Boto3Storage):
    bucket_name = settings.PERMANENT_S3_BUCKET_NAME
    access_key = settings.PERMANENT_S3_BUCKET_ACCESS_KEY_ID
    secret_key = settings.PERMANENT_S3_BUCKET_SECRET_ACCESS_KEY
