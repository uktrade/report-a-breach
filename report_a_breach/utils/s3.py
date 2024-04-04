import boto3
from django.conf import settings


def generate_presigned_url(bucket_name, object_key):
    """Generates a Presigned URL for the s3 object."""
    client = boto3.client("s3")
    presigned_url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_key},
        HttpMethod="GET",
        ExpiresIn=settings.PRE_SIGNED_URL_EXPIRY_SECONDS,
    )
    return presigned_url
