from datetime import datetime
from unittest.mock import MagicMock

from backend.src.chatgpt_integration.functions.delete_old_summary.app import handler


def test_successful_deletion(s3_chats, bucket_name_env):
    conn, file_name = s3_chats
    handler({}, MagicMock())

    results = conn.list_objects_v2(Bucket=bucket_name_env)

    assert (
        results["Contents"][0]["Key"]
        == f"buckup/{datetime.now().strftime('%Y.%m.%d')}/chats_for_gpt/random_file1.json"
    )
