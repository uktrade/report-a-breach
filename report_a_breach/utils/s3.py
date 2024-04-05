from django.conf import settings


def generate_presigned_url(s3_file_object):
    """Generates a Presigned URL for the s3 object."""
    presigned_url = s3_file_object.meta.client.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_file_object.bucket_name, "Key": s3_file_object.key},
        HttpMethod="GET",
        ExpiresIn=settings.PRESIGNED_URL_EXPIRY_SECONDS,
    )
    return presigned_url
