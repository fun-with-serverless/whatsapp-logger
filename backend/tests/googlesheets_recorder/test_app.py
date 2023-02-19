import json
import gspread  # type: ignore
from unittest.mock import patch, MagicMock
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from ...src.googlesheets_recorder.app import record_handler


def test_record_handler():
    with patch("gspread.service_account_from_dict"):
        record = MagicMock(SQSRecord)
        record.body = _get_body("test_group")

        sheet = MagicMock(gspread.spreadsheet.Spreadsheet)
        worksheet = MagicMock(gspread.spreadsheet.Worksheet)
        sheet.worksheet.return_value = worksheet
        sheet.add_worksheet.return_value = worksheet

        record_handler(record, sheet)
        sheet.worksheet.assert_called_once_with("test_group")
        worksheet.append_row.assert_called_once()
        assert worksheet.append_row.call_args[1]["values"] == [
            "2021-01-31T08:31:20",
            "test_group",
            "test_number",
            "test_name",
            "test_handle",
            "test_message",
            False,
        ]


def test_record_handler_group_is_empty_no_row_is_appended():
    with patch("gspread.service_account_from_dict"):
        record = MagicMock(SQSRecord)
        record.body = _get_body(" ")

        sheet = MagicMock(gspread.spreadsheet.Spreadsheet)
        worksheet = MagicMock(gspread.spreadsheet.Worksheet)
        sheet.worksheet.return_value = worksheet
        sheet.add_worksheet.return_value = worksheet

        record_handler(record, sheet)
        sheet.worksheet.assert_not_called()


def _get_body(group_name: str) -> str:
    return json.dumps(
        {
            "Message": '{{"group_name": "{group_name}", "group_id": "test_id", "time": 1612081880, "message": "test_message", "participant_id": "test_participant_id", "participant_handle": "test_handle", "participant_number": "test_number", "participant_contact_name": "test_name", "has_media": false}}'.format(
                group_name=group_name
            )
        }
    )
