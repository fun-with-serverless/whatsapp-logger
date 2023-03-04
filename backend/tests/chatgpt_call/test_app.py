import boto3
import moto  # type: ignore
import pytest
import json
from unittest.mock import MagicMock, patch

from backend.src.chatgpt_integration.functions.chatgpt_call.app import handler
from backend.tests.utils import MockOpenAi
from ...src.chatgpt_integration.functions.summerize_chats.app import (
    SUMMARY_PREFIX,
)


@pytest.fixture
def s3_chats(bucket_name_env):
    with moto.mock_s3():
        # set up the mock S3 environment
        conn = boto3.client("s3")
        conn.create_bucket(Bucket=bucket_name_env)

        file_name = f"{SUMMARY_PREFIX}/random_file1.json"
        conn.put_object(
            Bucket=bucket_name_env,
            Key=file_name,
            Body=f"{json.dumps({'group_name': 'gorup-name', 'group_id': 'group-id', 'chats': 'result is' })}",
        )

        yield conn, file_name


@patch("backend.src.chatgpt_integration.functions.chatgpt_call.app._get_openai")
def test_successful_call_to_chatgpt(get_open_ai, s3_chats, secret_manager):
    conn, file_name = s3_chats
    get_open_ai.return_value = MockOpenAi()
    result = handler({"file_name": file_name}, MagicMock())
    assert result == {
        "content": "haaa",
        "group_id": "group-id",
        "group_name": "gorup-name",
    }
