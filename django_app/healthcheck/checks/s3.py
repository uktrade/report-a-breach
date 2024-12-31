import boto3
import sentry_sdk

# from django_app.config import settings


def s3_check() -> bool:
    """
    Performs a check on the S3 connection
    """
    client = boto3.client("s3")

    bucket_names = ["temporary-document-bucket", "permanent-document-bucket"]

    try:
        for bucket_name in bucket_names:
            client.head_bucket(Bucket=bucket_name)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return False

    return True
