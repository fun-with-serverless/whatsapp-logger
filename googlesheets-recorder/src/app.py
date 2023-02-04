from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, batch_processor
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities import parameters
import gspread
from dacite import from_dict
from aws_lambda_powertools.utilities import parameters

import boto3
import os
import json
from dataclasses import dataclass
from datetime import datetime


logger = Logger()
processor = BatchProcessor(event_type=EventType.SQS)

@dataclass(frozen=True)
class WhatsAppMessage:
    group_name:str
    group_id: int
    time: datetime
    message: str
    participant_id: int
    participant_handle: str
    participant_number: str

def record_handler(record: SQSRecord, sheet: gspread.spreadsheet.Spreadsheet):
    payload: str = record.body
    worksheet_list = sheet.worksheets()
    # Get the last one.
    last_worksheet = worksheet_list[-1]
    if payload:
        message: WhatsAppMessage  = from_dict(data_class=WhatsAppMessage, data = json.loads(payload))
        last_worksheet.append_row(values=[message.time, message.group_name, message.participant_id, message.participant_handle, message.message])
        

        

GOOGLE_SECRET = parameters.get_secret(os.environ["GOOGLE_SECRET_AUTH_NAME"], transform="json")
G_SPREAD = gspread.service_account_from_dict(GOOGLE_SECRET)
GSHEET = G_SPREAD.open_by_url(parameters.get_parameter(os.environ["GOOGLE_SHEET_URL"]))
logger.info(f"Successfully loaded Google Sheets from {os.environ['GOOGLE_SHEET_URL']}")

@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext):
    
    batch = event["Records"]
    with processor(records=batch, handler=lambda record: record_handler(record, GSHEET)):
        processor.process()

    return processor.response()


