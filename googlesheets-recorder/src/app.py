from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, batch_processor
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities import parameters
import gspread
from dacite import from_dict, Config
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
    group_id: str
    time: datetime
    message: str
    participant_id: str
    participant_handle: str
    participant_number: str
    participant_contact_name: str
    

def record_handler(record: SQSRecord, sheet: gspread.spreadsheet.Spreadsheet):
    payload: str = record.body
    logger.debug(f"Retrieved {payload}")
    
    if payload:
        raw_message = json.loads(payload)["Message"]
        converter = lambda val: datetime.fromtimestamp(val)
        message: WhatsAppMessage  = from_dict(data_class=WhatsAppMessage, data = json.loads(raw_message), config=Config(type_hooks={datetime: converter}))
        group_sheet = _get_worksheet(sheet, message.group_name)
        group_sheet.append_row(values=[message.time.isoformat(), message.group_name, message.participant_number, message.participant_contact_name, message.participant_handle, message.message])
        

def _get_worksheet(sheet: gspread.spreadsheet.Spreadsheet, tab_name:str) -> gspread.spreadsheet.Worksheet:
    worksheet = None
    try:
        worksheet = sheet.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=tab_name, rows=20, cols=10)
        worksheet.append_row(values=["Date", "Group Name", "Participant Number", "Contact Name", "Participant Handle", "Message"])
        
    return worksheet


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


