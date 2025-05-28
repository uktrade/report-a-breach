import tempfile
from unittest.mock import patch

from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage
from report_a_suspected_breach.models import UploadedDocument
from utils.s3 import generate_presigned_url


def test_file_name(uploaded_document_object):
    uploaded_document_object.file.name = "directory/test/example.png"
    assert uploaded_document_object.file_name() == "example.png"


@patch("utils.s3.get_user_uploaded_files")
def test_save_documents(
    patched_user_uploaded_files, breach_object, rasb_client, delete_all_permanent_bucket_files, delete_all_temporary_bucket_files
):
    patched_user_uploaded_files.return_value = ["test1.png", "test2.png"]

    # first let's upload some files to s3.
    tmp_file_1 = tempfile.NamedTemporaryFile()
    tmp_file_1.write(b"test1")
    tmp_file_1.seek(0)

    tmp_file_2 = tempfile.NamedTemporaryFile()
    tmp_file_2.write(b"test2")
    tmp_file_2.seek(0)

    tmp_document_storage = TemporaryDocumentStorage()
    session = rasb_client.session
    tmp_document_storage.save(f"{session.session_key}/test1.png", tmp_file_1)
    tmp_document_storage.save(f"{session.session_key}/test2.png", tmp_file_2)

    perm_document_storage = PermanentDocumentStorage()
    assert len(list(perm_document_storage.bucket.objects.all())) == 0
    UploadedDocument.save_documents(rasb_client, breach=breach_object)
    assert len(list(perm_document_storage.bucket.objects.all())) == 2
    documents = breach_object.documents.all()
    assert len(documents) == 2
    assert documents[0].file_name() == "test1.png"
    assert documents[1].file_name() == "test2.png"
    assert documents[0].url() == generate_presigned_url(perm_document_storage, documents[0].file.name)
    assert documents[1].url() == generate_presigned_url(perm_document_storage, documents[1].file.name)
