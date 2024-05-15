from typing import Any

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from storages.backends.s3boto3 import S3Boto3Storage


def get_s3_client_from_storage(s3_storage: S3Boto3Storage) -> Any:
    """Get the S3 client object from the storage object."""
    return s3_storage.bucket.meta.client


def generate_presigned_url(s3_storage: Any, s3_file_object: Any) -> str:
    """Generates a Presigned URL for the s3 object."""

    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)

    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_storage.bucket_name, "Key": s3_file_object},
        HttpMethod="GET",
        ExpiresIn=settings.PRESIGNED_URL_EXPIRY_SECONDS,
    )
    return presigned_url


def get_all_session_files(s3_storage: S3Boto3Storage, session: SessionBase) -> dict[str, Any]:
    """Gets all files that a user has uploaded in a session."""
    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)
    response = s3_client.list_objects_v2(Bucket=s3_storage.bucket.name, Prefix=session.session_key)
    session_files = {}
    for content in response.get("Contents", []):
        file_name = content["Key"].rpartition("/")[2]

        # checking that a file with this name was uploaded in the session
        if file_name in session.get("file_uploads", []):
            session_files[file_name] = generate_presigned_url(
                s3_storage=s3_storage,
                s3_file_object=content["Key"],
            )
    return session_files


def get_breach_documents(s3_storage: S3Boto3Storage, breach_id: str) -> dict[str, Any]:
    """Gets all files associated with a breach."""
    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)
    response = s3_client.list_objects_v2(Bucket=s3_storage.bucket.name, Prefix=breach_id)
    breach_files = {}
    for content in response.get("Contents", []):
        file_name = content["Key"].rpartition("/")[2]
        breach_files[file_name] = generate_presigned_url(
            s3_storage=s3_storage,
            s3_file_object=content["Key"],
        )
    return breach_files


def delete_session_files(s3_storage: S3Boto3Storage, session: SessionBase) -> None:
    s3_client = get_s3_client_from_storage(s3_storage=s3_storage)

    response = s3_client.list_objects_v2(Bucket=s3_storage.bucket.name, Prefix=session.session_key)
    delete_keys = {"Objects": []}
    delete_keys["Objects"] = [{"Key": k} for k in [obj["Key"] for obj in response.get("Contents", [])]]
    s3_client.delete_objects(Bucket=s3_storage.bucket.name, Delete=delete_keys)
