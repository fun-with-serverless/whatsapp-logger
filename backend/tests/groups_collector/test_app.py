import os
from unittest.mock import MagicMock
from ...src.chatgpt_integration.functions.groups_collector.app import handler


def test_successful_group_collection(s3_raw_lake):
    handler({}, MagicMock())

    response = s3_chats.get_object(
        Bucket=os.environ["CHATS_BUCKET"], Key="chats_for_gpt/group-id-test.json"
    )

    content = response["Body"].read().decode("utf-8")

    assert (
        content
        == '{"group_name": "test", "group_id": "group-id", "chats": "Efi said Hello\\nEfi said Hi"}'
    )
