from datetime import datetime
import time
from unittest.mock import MagicMock
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from backend.src.utils.dynamodb_models import ApplicationState

from backend.tests.utils import get_sqs_body
from ...src.admin_panel.functions.messages_statistics.app import record_handler


def test_record_handler(application_state_db):
    record = MagicMock(SQSRecord)
    record.body = get_sqs_body("test_group", int(time.time()))

    record_handler(record)

    stats = ApplicationState.get_message_statistics()
    assert stats.total_today == 1
    assert stats.last_message_arrived.day == datetime.utcnow().day
    assert stats.last_message_arrived.year == datetime.utcnow().year
