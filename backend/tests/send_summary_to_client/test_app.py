from dataclasses import asdict
import json
from unittest.mock import MagicMock

import boto3

from backend.src.chatgpt_integration.functions.send_summary_to_client.app import handler
from backend.src.chatgpt_integration.utils.models import ChatGPTSummary
from backend.src.utils.client import DetailType
from backend.src.utils.db_models.whatsapp_groups import SummaryStatus, WhatsAppGroup


def test_group_found_summary_sent(events, group_db):
    WhatsAppGroup(
        "group-id", name="group-name", requires_daily_summary=SummaryStatus.MYSELF
    ).save()
    handler(asdict(ChatGPTSummary("Send", "group-name", "group-id")), MagicMock())

    sqs_client = boto3.client("sqs")
    sqs_response = sqs_client.receive_message(QueueUrl=events)
    for message in sqs_response["Messages"]:
        assert json.loads(message["Body"])["detail-type"] == DetailType.SUMMARY.value
        assert json.loads(message["Body"])["detail"]["send_to"] == "Myself"
        assert json.loads(message["Body"])["detail"]["group_id"] == "group-id"


def test_group_not_found_summary_not_sent(events, group_db):

    handler(asdict(ChatGPTSummary("Send", "group-name", "group-id")), MagicMock())

    sqs_client = boto3.client("sqs")
    sqs_response = sqs_client.receive_message(QueueUrl=events)
    assert "Messages" not in sqs_response


def test_requested_not_send_summary_not_sent(events, group_db):
    WhatsAppGroup(
        "group-id", name="group-name", requires_daily_summary=SummaryStatus.NONE
    ).save()

    handler(asdict(ChatGPTSummary("Send", "group-name", "group-id")), MagicMock())

    sqs_client = boto3.client("sqs")
    sqs_response = sqs_client.receive_message(QueueUrl=events)
    assert "Messages" not in sqs_response
