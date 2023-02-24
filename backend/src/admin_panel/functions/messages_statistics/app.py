import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    batch_processor,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

from ....utils.dynamodb_models import ApplicationState
from ....utils.models import WhatsAppMessage


logger = Logger()
processor = BatchProcessor(event_type=EventType.SQS)


def record_handler(record: SQSRecord):
    payload: str = record.body
    logger.debug(f"Retrieved {payload}")

    if payload:
        raw_message = json.loads(payload)["Message"]
        message = WhatsAppMessage.from_json(raw_message=raw_message)

        if message.group_name.strip():
            ApplicationState.update_new_message_arrived(message.time)


@batch_processor(record_handler=record_handler, processor=processor)
@logger.inject_lambda_context(log_event=True)
def handler(event, context: LambdaContext):
    return processor.response()
