from datetime import datetime, timezone
from typing import Dict
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from pynamodb.exceptions import PutError
from ..utils.db_models.whatsapp_groups import WhatsAppGroup
from ..utils.chats_data_lake import AggregatedGroup, ChatsDataLake

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event: dict, context: LambdaContext):
    lake = ChatsDataLake()
    today = datetime.now(tz=timezone.utc)
    groups: Dict[str, AggregatedGroup] = lake.get_all_chats(today)

    for key, value in groups.items():
        try:
            # Conditional save
            WhatsAppGroup(value.group_id, name=value.group_name).save(
                WhatsAppGroup.id.does_not_exist()
            )
        except PutError as err:
            if err.cause_response_code != "ConditionalCheckFailedException":
                raise err
            else:
                logger.debug("Failed saving group due to conditional check error")
