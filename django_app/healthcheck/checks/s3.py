import boto3
import sentry_sdk

from django_app.config import settings


def s3_check() -> bool:
    """
    Performs a check on the S3 connection
    """
    client = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME)

    bucket_names = [settings.TEMPORARY_S3_BUCKET_NAME, settings.PERMANENT_S3_BUCKET_NAME]

    try:
        for bucket_name in bucket_names:
            client.head_bucket(Bucket=bucket_name)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return False

    return True
