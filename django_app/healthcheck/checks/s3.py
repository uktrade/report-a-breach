import sentry_sdk
from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage


def s3_check() -> bool:
    """
    Performs a check on the S3 connection
    """
    temporary_document_bucket = TemporaryDocumentStorage().bucket
    permanent_document_bucket = PermanentDocumentStorage().bucket

    try:
        assert temporary_document_bucket.creation_date
        assert permanent_document_bucket.creation_date
        return True
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return False
