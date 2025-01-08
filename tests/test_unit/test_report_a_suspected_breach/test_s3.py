from unittest.mock import MagicMock, Mock, patch

from django.core.cache import cache
from utils.s3 import get_all_session_files


@patch("utils.s3.get_s3_client_from_storage")
def test_get_all_session_files(mocked_get_s3_client):
    mocked_get_s3_client.return_value = MagicMock()
    mocked_get_s3_client.return_value.list_objects_v2 = MagicMock(return_value={"Contents": [{"Key": "test.png"}]})

    session_object = MagicMock()
    session_object.is_empty = MagicMock(return_value=False)
    session_object.get = MagicMock(return_value=["test.png"])

    session_object.session_key = "test_session_key"
    redis_cache_key = f"{session_object.session_key}"
    cache.set(redis_cache_key, "test.png")

    session_files = get_all_session_files(Mock(), session_object)
    assert len(session_files) == 1
    assert "test.png" in session_files


@patch("utils.s3.get_s3_client_from_storage")
def test_no_session_returns_empty_session_files(mocked_get_s3_client):
    mocked_get_s3_client.return_value = MagicMock()
    mocked_get_s3_client.return_value.list_objects_v2 = MagicMock(return_value={"Contents": [{"Key": "test.png"}]})

    session_object = MagicMock()
    session_object.is_empty = MagicMock(return_value=True)
    session_object.get = MagicMock(return_value=["test.png"])

    session_object.session_key = "test_session_key"
    redis_cache_key = f"{session_object.session_key}"
    cache.set(redis_cache_key, "test.png")

    session_files = get_all_session_files(Mock(), session_object)
    assert len(session_files) == 0
