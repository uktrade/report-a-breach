from unittest.mock import MagicMock, Mock, patch

from utils.s3 import get_all_session_files


@patch("utils.s3.get_s3_client_from_storage")
def test_get_all_session_files(mocked_get_s3_client):
    mocked_get_s3_client.return_value = MagicMock()
    mocked_get_s3_client.return_value.list_objects_v2 = MagicMock(return_value={"Contents": [{"Key": "test.png"}]})

    session_object = MagicMock()
    session_object.get = MagicMock(return_value=["test.png"])
    session_object.session_key = "test_session_key"

    session_files = get_all_session_files(Mock(), session_object)
    assert len(session_files) == 1
    assert "test.png" in session_files
