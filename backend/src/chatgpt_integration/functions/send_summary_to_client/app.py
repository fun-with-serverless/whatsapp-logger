from __future__ import annotations
from dataclasses import asdict
from dacite import from_dict
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from ....utils.client import Client, DetailType, Source

from ....utils.db_models.whatsapp_groups import SummaryStatus, WhatsAppGroup
from ...utils.models import ChatGPTSummary

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):
    summary = from_dict(data_class=ChatGPTSummary, data=event)
    client = Client()
    try:
        group = WhatsAppGroup.get(summary.group_id)
        if group.requires_daily_summary != SummaryStatus.NONE:
            detail = asdict(summary)
            detail["send_to"] = group.requires_daily_summary.value
            detail["send_to_group_id"] = (
                group.send_summary_to_group_id
                if "send_summary_to_group_id" in group.attribute_values
                else None
            )
            client.send_message(
                detail_type=DetailType.SUMMARY, source=Source.CHATGPT, detail=detail
            )
    except WhatsAppGroup.DoesNotExist:
        logger.info("Group not found, ignoring...", summary=asdict(summary))
