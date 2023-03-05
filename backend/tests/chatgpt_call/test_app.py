from unittest.mock import MagicMock, patch

from backend.src.chatgpt_integration.functions.chatgpt_call.app import handler
from backend.tests.utils import MockOpenAi


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
