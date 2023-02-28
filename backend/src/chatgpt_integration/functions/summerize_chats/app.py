from __future__ import annotations
from collections import defaultdict

from dataclasses import dataclass
from datetime import datetime, timezone
import functools
import json
import os
from typing import Dict, List
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from mypy_boto3_s3.service_resource import Bucket

from ....utils.models import WhatsAppMessage

logger = Logger()


@dataclass(frozen=True)
class AggregatedChat:
    participant_name: str
    time_of_chat: datetime
    message: str


@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):
    bucket = _get_s3_bucket()
    chats = _collect_chats(bucket=bucket)
    _write_to_s3(chats, bucket)


@functools.cache
def _get_s3_bucket() -> Bucket:
    s3 = boto3.resource("s3")
    return s3.Bucket(os.environ["CHATS_BUCKET"])


def _collect_chats(bucket: Bucket) -> Dict[str, List[AggregatedChat]]:
    name_to_messages: Dict[str, List[AggregatedChat]] = defaultdict(list)
    now = datetime.now(tz=timezone.utc)
    for file_obj in bucket.objects.filter(Prefix=f"{now.strftime('%Y.%m.%d')}"):
        file_content = file_obj.get()["Body"]
        for line in file_content.iter_lines():
            message: WhatsAppMessage = WhatsAppMessage.from_json(line.decode())
            group_identifier = f"{message.group_id}-{message.group_name}"
            chat = AggregatedChat(
                message.participant_name, message.time, message=message.message
            )

            name_to_messages[group_identifier].append(chat)
    return name_to_messages


def _write_to_s3(chats: Dict[str, List[AggregatedChat]], bucket: Bucket) -> None:
    """
    Writes the aggregated chat messages to S3 in the specified format.

    Args:
        chats: A dictionary mapping a unique identifier for each chat group to a list
            of `AggregatedChat` objects containing aggregated chat messages for that group.
        bucket: A `Bucket` object representing the S3 bucket to write the chats to.

    Returns:
        None.

    """
    for group_identifier, chat_list in chats.items():
        group_dict = {"group_name": group_identifier, "chats": str}

        chats_str = "\n".join(
            [
                f"{chat.time_of_chat}$${chat.participant_name}$${chat.message}"
                for chat in chat_list
            ]
        )

        group_dict["chats"] = chats_str

        # Convert the group dictionary to a JSON string and write to S3
        file_name = f"chats_for_gpt/{group_identifier}.json"
        file_content = json.dumps(group_dict)
        bucket.put_object(Key=file_name, Body=file_content)
