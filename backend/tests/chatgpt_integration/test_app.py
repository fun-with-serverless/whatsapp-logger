import os
from unittest.mock import MagicMock
import botocore

import pytest

from backend.src.utils.db_models.whatsapp_groups import SummaryStatus, WhatsAppGroup
from ...src.chatgpt_integration.functions.summerize_chats.app import handler


def test_successful_chatgpt_summerize_creation(s3_raw_lake, group_db):
    WhatsAppGroup(
        "group-id", name="group-name", requires_daily_summary=SummaryStatus.MYSELF
    ).save()

    handler({}, MagicMock())

    response = s3_raw_lake.get_object(
        Bucket=os.environ["CHATS_BUCKET"], Key="chats_for_gpt/group-id-test.json"
    )

    content = response["Body"].read().decode("utf-8")

    assert (
        content
        == '{"group_name": "test", "group_id": "group-id", "chats": "Efi said Hello\\nEfi replied to Anat with Hi"}'
    )


def test_group_does_not_require_summerize_file_not_created(s3_raw_lake, group_db):
    WhatsAppGroup("group-id", name="group-name").save()

    handler({}, MagicMock())

    with pytest.raises(botocore.exceptions.ClientError):
        s3_raw_lake.get_object(
            Bucket=os.environ["CHATS_BUCKET"], Key="chats_for_gpt/group-id-test.json"
        )


def test_group_not_found_file_not_created(s3_raw_lake, group_db):
    handler({}, MagicMock())

    with pytest.raises(botocore.exceptions.ClientError):
        s3_raw_lake.get_object(
            Bucket=os.environ["CHATS_BUCKET"], Key="chats_for_gpt/group-id-test.json"
        )
