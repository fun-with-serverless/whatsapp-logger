from datetime import datetime, timedelta, timezone
from typing import Dict
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from ..utils.db_models.whatsapp_groups import WhatsAppGroup
from ..utils.chats_data_lake import AggregatedGroup, ChatsDataLake

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event: dict, context: LambdaContext):
    lake = ChatsDataLake()
    yesterday = datetime.now(tz=timezone.utc) - timedelta(days=1)
    groups: Dict[str, AggregatedGroup] = lake.get_all_chats(yesterday)

    for key, value in groups.items():
        # Conditional save
        WhatsAppGroup(value.group_id, name=value.group_name).save(
            WhatsAppGroup.id.does_not_exist()
        )
