from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import functools
import os
from typing import List, TYPE_CHECKING, Optional
import boto3
from typing import Dict

from .models import WhatsAppMessage

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Bucket


@functools.cache
def _get_s3_bucket() -> "Bucket":
    s3 = boto3.resource("s3")
    return s3.Bucket(os.environ["CHATS_BUCKET"])


@dataclass(frozen=True)
class AggregatedChat:
    participant_name: str
    time_of_chat: datetime
    message: str
    quoted: Optional[str] = None


@dataclass
class AggregatedGroup:
    chats: List[AggregatedChat] = field(default_factory=list)
    group_name: str = ""
    group_id: str = ""


class ChatsDataLake:
    def __init__(self):
        self.bucket = _get_s3_bucket()

    def get_all_chats(self, day: datetime) -> Dict[str, AggregatedGroup]:
        groups: Dict[str, AggregatedGroup] = defaultdict(AggregatedGroup)

        for file_obj in self.bucket.objects.filter(
            Prefix=f"{day.strftime('%Y.%m.%d')}"
        ):
            file_content = file_obj.get()["Body"].read().decode("utf-8")
            for line in file_content.splitlines():
                message: WhatsAppMessage = WhatsAppMessage.from_json(line)
                chat = AggregatedChat(
                    message.participant_name,
                    message.time,
                    message=message.message,
                    quoted=message.quoted_message_participant_name,
                )
                key = f"{message.group_id}-{message.group_name}"
                groups[key].chats.append(chat)
                groups[key].group_id = message.group_id
                groups[key].group_name = message.group_name

        return groups
