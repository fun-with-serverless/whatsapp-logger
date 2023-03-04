import os
import boto3
import moto  # type: ignore
import pytest
from dataclasses import asdict
import json
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone
from ...src.chatgpt_integration.functions.summerize_chats.app import handler
from backend.src.utils.models import WhatsAppMessage


@pytest.fixture
def s3_chats(bucket_name_env):
    def to_epoch(val: datetime) -> int:
        return int(val.timestamp())

    with moto.mock_s3():
        # set up the mock S3 environment
        conn = boto3.client("s3")
        conn.create_bucket(Bucket=bucket_name_env)
        yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
        message1 = WhatsAppMessage(
            "test",
            "group-id",
            datetime(year=2023, month=1, day=10, hour=23, minute=23),
            "Hello",
            "participant-id",
            participant_handle="Efi",
            participant_number="123456",
            has_media=False,
        )

        message2 = WhatsAppMessage(
            "test",
            "group-id",
            datetime(year=2023, month=1, day=10, hour=23, minute=24),
            "Hi",
            "participant-id",
            participant_handle="Efi",
            participant_number="123456",
            has_media=False,
        )

        conn.put_object(
            Bucket=bucket_name_env,
            Key=f"{yesterday.strftime('%Y.%m.%d')}/random_file1",
            Body=f"{json.dumps(asdict(message1), default=to_epoch)}\n",
        )

        conn.put_object(
            Bucket=bucket_name_env,
            Key=f"{yesterday.strftime('%Y.%m.%d')}/random_file2",
            Body=f"{json.dumps(asdict(message2), default=to_epoch)}\n",
        )

        yield conn


def test_successful_chatgpt_summerize_creation(s3_chats):
    handler({}, MagicMock())

    response = s3_chats.get_object(
        Bucket=os.environ["CHATS_BUCKET"], Key="chats_for_gpt/group-id-test.json"
    )

    content = response["Body"].read().decode("utf-8")

    assert (
        content
        == '{"group_name": "test", "group_id": "group-id", "chats": "Efi said Hello\\nEfi said Hi"}'
    )
