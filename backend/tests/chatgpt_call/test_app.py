from unittest.mock import MagicMock, patch
import pytest
from backend.src.chatgpt_integration.functions.chatgpt_call.app import (
    _find_max_substring,
    handler,
)
from backend.tests.utils import MockOpenAi


@patch("backend.src.chatgpt_integration.functions.chatgpt_call.app._get_openai")
def test_successful_call_to_chatgpt(get_open_ai, s3_chats, group_db, secret_manager):
    conn, file_name = s3_chats
    get_open_ai.return_value = MockOpenAi()
    result = handler({"file_name": file_name}, MagicMock())
    assert result == {
        "content": "haaa",
        "group_id": "group-id",
        "group_name": "gorup-name",
    }


@pytest.mark.parametrize(
    "my_string, max_magic_value, expected",
    [
        # Test when the entire string meets the requirement
        ("abcdef", 1000, "abcdef"),
        # Test when only the first character meets the requirement
        ("abcdef", 10, "a"),
        # Test when no characters meet the requirement
        ("abcdef", 0, ""),
        # Test when some characters meet the requirement
        ("abcdef", 35, "abc"),  # Assuming the magic value of "abc" is less than 4000
        # Test when the string is empty
        ("", 1000, ""),
    ],
)
def test_find_max_substring(my_string, max_magic_value, expected):
    def magic_function(string):
        return len(string) * 10

    assert _find_max_substring(my_string, magic_function, max_magic_value) == expected
