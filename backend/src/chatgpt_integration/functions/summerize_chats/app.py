from __future__ import annotations
from collections import defaultdict

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import functools
import json
import os
from typing import TYPE_CHECKING, Dict, List
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Bucket

from ....utils.models import WhatsAppMessage

logger = Logger()
SUMMARY_PREFIX = "chats_for_gpt"


@dataclass(frozen=True)
class AggregatedChat:
    participant_name: str
    time_of_chat: datetime
    message: str


@dataclass
class AggregatedGroup:
    chats: List[AggregatedChat] = field(default_factory=list)
    group_name: str = ""
    group_id: str = ""


@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):
    bucket = _get_s3_bucket()
    chats = _collect_chats(bucket=bucket)
    files = _write_to_s3(chats, bucket)
    return {"s3_files": files}


@functools.cache
def _get_s3_bucket() -> Bucket:
    s3 = boto3.resource("s3")
    return s3.Bucket(os.environ["CHATS_BUCKET"])


def _collect_chats(bucket: Bucket) -> Dict[str, AggregatedGroup]:
    groups: Dict[str, AggregatedGroup] = defaultdict(AggregatedGroup)
    yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
    for file_obj in bucket.objects.filter(Prefix=f"{yesterday.strftime('%Y.%m.%d')}"):
        file_content = file_obj.get()["Body"].read().decode("utf-8")
        for line in file_content.splitlines():
            message: WhatsAppMessage = WhatsAppMessage.from_json(line)
            chat = AggregatedChat(
                message.participant_name, message.time, message=message.message
            )
            key = f"{message.group_id}-{message.group_name}"
            groups[key].chats.append(chat)
            groups[key].group_id = message.group_id
            groups[key].group_name = message.group_name

    logger.info("Appended chats", count=len(groups))
    return groups


def _write_to_s3(groups: Dict[str, AggregatedGroup], bucket: Bucket) -> List[dict]:
    files_to_return: List[dict] = []
    for group in groups:
        group_dict = {
            "group_name": groups[group].group_name,
            "group_id": groups[group].group_id,
            "chats": "",
        }

        sorted_chats = sorted(groups[group].chats, key=lambda val: val.time_of_chat)
        chats_str = "\n".join(
            [f"{chat.participant_name} said {chat.message}" for chat in sorted_chats]
        )

        group_dict["chats"] = chats_str
        file_name = f"{groups[group].group_id}-{groups[group].group_name}.json".replace(
            "/", "_"
        )
        # Convert the group dictionary to a JSON string and write to S3
        file_name = f"{SUMMARY_PREFIX}/{file_name}"
        file_content = json.dumps(group_dict)
        bucket.put_object(Key=file_name, Body=file_content.encode())
        files_to_return.append({"file_name": file_name})
    return files_to_return
