import boto3
import sentry_sdk
from django.conf import settings


def s3_check() -> bool:
    """
    Check if the S3 bucket exists and ensure the app can access it.
    https://boto3.amazonaws.com/v1/documentation/api/1.35.9/reference/services/s3/client/head_bucket.html
    """
    client = boto3.client("s3")

    bucket_names = [settings.TEMPORARY_S3_BUCKET_NAME, settings.PERMANENT_S3_BUCKET_NAME]

    try:
        for bucket_name in bucket_names:
            client.head_bucket(Bucket=bucket_name)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return False

    return True
