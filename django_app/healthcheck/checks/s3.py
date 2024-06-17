from botocore.exceptions import EndpointConnectionError
from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage


def s3_check() -> bool:
    """
    Performs a basic check on the S3 connection
    """
    temporary_document_bucket = TemporaryDocumentStorage().bucket
    permanent_document_bucket = PermanentDocumentStorage().bucket
    try:
        assert temporary_document_bucket
        assert permanent_document_bucket
        return True
    except EndpointConnectionError:
        return False
