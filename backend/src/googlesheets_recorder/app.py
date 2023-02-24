from ..utils.models import WhatsAppMessage

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities import parameters
import gspread  # type: ignore
from dacite import from_dict, Config

import os
import json
from dataclasses import dataclass, field
from datetime import datetime
import functools
from typing import Optional

logger = Logger()
processor = BatchProcessor(event_type=EventType.SQS)


@dataclass(frozen=True)
class WhatsAppMessage:
    group_name: str
    group_id: str
    time: datetime
    message: str
    participant_id: str
    participant_handle: str
    participant_number: str
    has_media: bool
    participant_contact_name: Optional[str] = field(default="Unknown")


def record_handler(record: SQSRecord, sheet: gspread.spreadsheet.Spreadsheet):
    payload: str = record.body
    logger.debug(f"Retrieved {payload}")

    if payload:
        raw_message = json.loads(payload)["Message"]

        def converter(val):
            return datetime.fromtimestamp(val)

        message: WhatsAppMessage = from_dict(
            data_class=WhatsAppMessage,
            data=json.loads(raw_message),
            config=Config(type_hooks={datetime: converter}),
        )
        if message.group_name.strip():
            group_sheet = _get_worksheet(sheet, message.group_name)
            group_sheet.append_row(
                values=[
                    message.time.isoformat(),
                    message.group_name,
                    message.participant_number,
                    message.participant_contact_name,
                    message.participant_handle,
                    message.message,
                    message.has_media,
                ]
            )


def _get_worksheet(
    sheet: gspread.spreadsheet.Spreadsheet, tab_name: str
) -> gspread.spreadsheet.Worksheet:
    worksheet = None
    try:
        worksheet = sheet.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=tab_name, rows=20, cols=10)
        worksheet.append_row(
            values=[
                "Date",
                "Group Name",
                "Participant Number",
                "Contact Name",
                "Participant Handle",
                "Message",
                "Has media?",
            ]
        )

    return worksheet


@functools.cache
def _get_get_google_sheet_object() -> gspread.spreadsheet.Spreadsheet:
    google_secret = parameters.get_secret(
        os.environ["GOOGLE_SECRET_AUTH_NAME"], transform="json"
    )
    google_spread = gspread.service_account_from_dict(google_secret)
    logger.info(
        f"Successfully loaded Google Sheets from {os.environ['GOOGLE_SHEET_URL']}"
    )
    return google_spread.open_by_url(
        parameters.get_parameter(os.environ["GOOGLE_SHEET_URL"])
    )


@logger.inject_lambda_context
def handler(event: dict, context: LambdaContext):

    batch = event["Records"]
    with processor(
        records=batch,
        handler=lambda record: record_handler(record, _get_get_google_sheet_object()),
    ):
        processor.process()

    return processor.response()
