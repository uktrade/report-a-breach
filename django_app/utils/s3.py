from typing import Any

from django.conf import settings


def generate_presigned_url(s3_client_object: Any, s3_file_object: Any) -> str:
    """Generates a Presigned URL for the s3 object."""
    presigned_url = s3_client_object.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_file_object.bucket_name, "Key": s3_file_object.key},
        HttpMethod="GET",
        ExpiresIn=settings.PRESIGNED_URL_EXPIRY_SECONDS,
    )
    return presigned_url
