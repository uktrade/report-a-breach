from botocore.exceptions import EndpointConnectionError
from storages.backends.s3 import S3Storage


def s3_check() -> bool:
    """
    Performs a basic check on the S3 connection
    """
    # todo - implement checks for both the STATIC and PRIVATE buckets
    # S3Storage().connection.Bucket(STATIC_BUCKET_NAME).creation_date
    # S3Storage().connection.Bucket(PRIVATE_BUCKET_NAME).creation_date
    bucket = S3Storage().bucket
    try:
        assert bucket.creation_date
        return True
    except EndpointConnectionError:
        return False
