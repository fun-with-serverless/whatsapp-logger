from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from typing import TYPE_CHECKING, Dict, List
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from ....utils.db_models.whatsapp_groups import SummaryStatus, WhatsAppGroup

from ....utils.chats_data_lake import AggregatedChat, AggregatedGroup, ChatsDataLake

from ...utils.consts import SUMMARY_PREFIX

if TYPE_CHECKING:
    from mypy_boto3_s3.service_resource import Bucket


logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):
    lake = ChatsDataLake()
    chats = _collect_chats(lake)
    files = _write_to_s3(chats, lake.bucket)
    return {"s3_files": files}


def _collect_chats(lake: ChatsDataLake) -> Dict[str, AggregatedGroup]:
    yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
    return_value = lake.get_all_chats(yesterday)
    logger.info("Appended chats", count=len(return_value))

    return return_value


def _write_to_s3(groups: Dict[str, AggregatedGroup], bucket: Bucket) -> List[dict]:
    files_to_return: List[dict] = []
    for group_id, group in groups.items():
        try:
            db_group = WhatsAppGroup.get(group.group_id)
            if db_group.requires_daily_summary == SummaryStatus.NONE:
                logger.debug(
                    "No need to summarize",
                    group_id=group.group_id,
                    group_name=group.group_name,
                )
                continue
        except WhatsAppGroup.DoesNotExist:
            logger.warning(
                "Group not found. No need to summarize",
                group_id=group.group_id,
                group_name=group.group_name,
            )
            continue

        group_dict = {
            "group_name": group.group_name,
            "group_id": group.group_id,
            "chats": "",
        }

        sorted_chats = sorted(group.chats, key=lambda val: val.time_of_chat)

        def create_summary(chat: AggregatedChat):
            if chat.quoted:
                return f"{chat.participant_name} replied to {chat.quoted} with {chat.message}"

            return f"{chat.participant_name} said {chat.message}"

        chats_str = "\n".join(map(create_summary, sorted_chats))

        group_dict["chats"] = chats_str
        file_name = f"{group.group_id}-{group.group_name}.json".replace("/", "_")
        # Convert the group dictionary to a JSON string and write to S3
        file_name = f"{SUMMARY_PREFIX}/{file_name}"
        file_content = json.dumps(group_dict)
        bucket.put_object(Key=file_name, Body=file_content.encode())
        files_to_return.append({"file_name": file_name})
    return files_to_return
