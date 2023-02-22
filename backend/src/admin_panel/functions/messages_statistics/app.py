import os
import json
from datetime import datetime
import functools

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    batch_processor
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities import parameters
from dacite import from_dict, Config
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
            pass



@batch_processor(record_handler=record_handler, processor=processor)
def lambda_handler(event, context: LambdaContext):
    return processor.response()
